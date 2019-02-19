from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from user.models import User


# Create your views here.
def register(request):
    '''注册'''
    if request.method == 'GET':
        # 显示注册页面
        return render(request, 'register.html')
    else:
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

        # 返回应答，跳转到首页
        return redirect(reverse('goods:index'))


'''
def register_handle(request):
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
        return render(request, 'register.html', {'errmsg':'用户名已存在'})

    # 业务处理
    user = User.objects.create_user(username, email, password)
    user.is_active = 0
    user.save()

    # 返回应答，跳转到首页
    return redirect(reverse('goods:index'))
'''