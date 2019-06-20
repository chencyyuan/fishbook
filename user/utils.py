#向网易云信发送请求，帮助后台发送短信
import hashlib
import os
import uuid
from time import time

import requests
import json

from django.core.mail import send_mail
from qiniu import Auth, put_file, put_data

from fishbook.settings import EMAIL_HOST_USER, MEDIA_ROOT
from user.models import UserProfile

#发送短信息
def util_sendmsg(mobile):
    url='https://api.netease.im/sms/sendcode.action'
    data={'mobile':mobile}
    #4 部分组成  headers:AppKey Nonce CurTime CheckSum
    AppKey='ea02649d2cd22876328076c791b4fc54'
    Nonce='dhsudhuwha2452bbh13919jxs81'
    CurTime=str(time())
    AppSecret='3313367aaead'
    content=AppSecret+Nonce+CurTime
    CheckSum=hashlib.sha1(content.encode('utf-8')).hexdigest()

    headers={'AppKey':AppKey,'Nonce':Nonce,'CurTime':CurTime,'CheckSum':CheckSum}

    response=requests.post(url,data,headers=headers)
    #json
    str_result=response.text  #获取响应体
    json_result=json.loads(str_result) #转成json
    return json_result

#发送邮件
def send_email(email,request,user):
    subject='个人鱼书账户找回密码'
    # user=UserProfile.objects.filter(email=email).first()
    ran_code=uuid.uuid4()
    ran_code=str(ran_code)
    ran_code=ran_code.replace('-','')
    print(user.id)
    request.session[ran_code]=user.id
    message='''
        亲爱的用户：
                您好！此链接用于找回密码，请点击链接：<a href='http://127.0.0.1:8000/user/update_pwd?c=%s'>更新密码</a>，
                如果链接不能点击，请复制：
                http://127.0.0.1:8000/user/update_pwd?c=%s
            个人鱼书团队
    '''%(ran_code,ran_code)
    result=send_mail(subject,"",EMAIL_HOST_USER,[email,],html_message=message)
    return result

#上传图片到七牛云
def upload_image(storeobj):
    access_key='Iti8rKoa9Ey3rOJlGgz0zaCT58kvqN47Qy2m6jh6'
    secret_key='Lju4wCmZe52Zkp3sgFTqgx_QSy9MKsws36uWVeMV'

    #构建鉴权对象
    q=Auth(access_key,secret_key)

    #要上传的空间
    bucket_name='myblog'

    #上传后保存的文件名
    key=storeobj.name
    #生成上传Token,可以指定过期时间等
    token= q.upload_token(bucket_name,key,3600)

    #要上传文件的本地路径
    # localfile=os.path.join(MEDIA_ROOT,imagepath)
    ret,info=put_data(token,key,storeobj.read())  #put_data不用从本地读图片

    # print(ret,info)
    filename=ret.get('key')
    # save_path='http://pr6lg0gah.bkt.clouddn.com/'+filename
    save_path='http://www.chenyyuan.com/'+filename
    return save_path

