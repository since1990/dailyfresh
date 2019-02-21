from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.http import HttpResponse
from user.models import User, Address
from celery_tasks.tasks import send_register_email  # 分布式发送激活邮件
from django.contrib.auth import authenticate, login, logout  # 用户的认证
from utils.mixin import LoginRequiredMixin
import re


# Create your views here.
class RegisterView(View):
    def get(self, request):
        # 显示注册页面
        return render(request, 'register.html')

    def post(self, request):
        # 进行注册处理
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        # 数据校验
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 说明用户名不存在
            user = None

        if user:
            # 满足条件说明用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 业务处理
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送激活邮件
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode()
        send_register_email.delay(email, username, token)

        # 返回应答，跳转到首页
        return redirect(reverse('goods:index'))


class ActiveView(View):
    '''进行用户激活'''
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 跳转到登陆页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


class LoginView(View):
    '''登陆页面'''
    def get(self, request):
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # 数据校验
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})
        # 内置的账户认证
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户的登陆状态
                login(request, user)
                # 获取要跳转的url
                next_url = request.GET.get('next', reverse('goods:index'))  # 设置默认值-跳转到首页

                response = redirect(next_url)
                # 判断是否需要记住用户名
                rem = request.POST.get('remember')
                if rem == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '用户未激活'})
        else:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


class LogoutView(View):
    '''退出登陆'''
    def get(self, request):
        logout(request)
        # 跳转到首页
        return redirect(reverse('goods:index'))


class UserInfoView(LoginRequiredMixin, View):
    '''用户中心-信息页'''
    def get(self, request):
        user = request.user
        address = Address.objects.get_default_address(user)
        return render(request, 'user_center_info.html', {'page': 'user', 'address': address})


class UserOrderView(LoginRequiredMixin, View):
    '''用户中心-订单页'''
    def get(self, request):
        user = request.user
        return render(request, 'user_center_order.html', {'page': 'order'})


class AddressView(LoginRequiredMixin, View):
    '''用户中心-地址页'''
    def get(self, request):
        user = request.user  # 获取登陆用户对应的user对象
        # 获取用户的默认收货地址
        address = Address.objects.get_default_address(user)
        return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机号格式不正确'})

        user = request.user  # 获取登陆用户对应的user对象
        # 获取用户的默认收货地址
        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        # 添加地址信息
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               phone=phone,
                               zip_code=zip_code,
                               is_default=is_default)
        # 返回应答，刷新页面
        return redirect(reverse('user:address'))
