import uuid

from celery import shared_task
from django.core.mail import send_mail
from rest_framework import request

from fishbook.settings import EMAIL_HOST_USER
from user.models import UserProfile


@shared_task
def sendmail(email, uid):
    print('123123',uid, email)
    subject = '密码找回'
    message = '''
        可爱的用户:<br>
                &nbsp;&nbsp;您好！<br>此链接用户找回密码，请点击链接: <a href='http://127.0.0.1:8000/user/update_pwd?c=%s'>更新密码</a>，
                如果链接不能点击，请复制：
                 http://127.0.0.1:8000/user/update_pwd?c=%s
               鱼书团队
    ''' % (uid, uid)
    print('----->1', message)
    send_mail(subject, message='', from_email=EMAIL_HOST_USER, recipient_list=[email, ], html_message=message)
