from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
import time
# 在任务处理端加上以下代码
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
django.setup()

# 创建一个celery实例对象
app = Celery('celery_tasks.tasks', broker='redis://192.168.80.130:6379/10')

# 定义任务函数
@app.task  # 调用实例对象的task函数进行装饰
def send_register_email(to_email, username, token):
    '''发送激活邮件'''
    subject = '天天生鲜欢迎信息！'
    message = ''
    html_message = '''<h1>%s，欢迎您成为我们天天生鲜会员，请点击以下链接激活您的账户</h1><br>
                         <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>''' % (
    username, token, token)
    send_mail(subject, message, from_email=settings.EMAIL_FROM, recipient_list=[to_email], html_message=html_message)
