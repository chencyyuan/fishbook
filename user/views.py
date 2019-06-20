import uuid

from captcha.models import CaptchaStore
from django.contrib.auth import logout,login,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.cache import cache
from user.task import sendmail

# Create your views here.
from django.urls import reverse


from user.forms import LoginForm, UserRegisterForm, CaptchaTestForm
from user.models import UserProfile
# from user.utils import util_sendmsg, send_email, upload_image
from user.utils import send_email, util_sendmsg


def user_register(request):
    if request.method == 'GET':
        return render(request,'user/register.html')
    else:
        rform = UserRegisterForm(request.POST)  # 使用form获取数据
        if rform.is_valid():  # 进行数据的校验
            # 从干净的数据中取值
            username = rform.cleaned_data.get('username')
            email = rform.cleaned_data.get('email')
            mobile = rform.cleaned_data.get('mobile')
            password = rform.cleaned_data.get('password')
            if not UserProfile.objects.filter(Q(username=username) | Q(email=email)).exists():
                # 注册到数据库中
                password = make_password(password)  # 密码加密
                user = UserProfile.objects.create(username=username, password=password, email=email,mobile=mobile)
                if user:
                    return render(request,'user/login.html')
            else:
                return render(request, 'user/register.html', context={'msg': '用户名或者手机号码已经存在！'})
        return render(request, 'user/register.html', context={'msg': '注册失败，重新填写！','errors':rform.errors})


#登录
def user_login(request):
    if request.method=='GET':
        return render(request,'user/login.html')
    else:
        lform=LoginForm(request.POST)
        if lform.is_valid():
            email=lform.cleaned_data.get('email')
            # password=lform.cleaned_data.get('password')
            #进行数据库的查询
            user=UserProfile.objects.filter(email=email).first()

            #前提是继承了AbstractUser
            # user=authenticate(email=email,password=password)
            if user:
                res=login(request,user) # # 将用户对象保存在底层的request中  （session）
                return redirect(reverse('index')) #
        return render(request,'user/login.html',context={'errors':lform.errors})

# #忘记密码
# def forget_password(request):
#     if request.method=='GET':
#         form=CaptchaTestForm()
#         return render(request,'user/password.html',context={'form':form})
#     else:
#         # 获取提交的邮箱，发送邮件,通过发送的邮箱连接设置新的密码
#         email=request.POST.get('email')
#         user=UserProfile.objects.filter(email=email).first()
#         if user:
#             #给此邮箱地址发送邮件
#             result=send_email(email,request,user)
#             if result:
#                 return HttpResponse("邮件发送成功！请尽快去邮箱更改密码！<a href='/'>返回首页>>></a>")
#         else:
#             return render(request,'user/password.html',context={'msg':'该邮箱不存在！'})
#     return render(request,'user/password.html')

# 忘记密码---- 异步发送邮件
def forget_password(request):
    if request.method == 'GET':
        form = CaptchaTestForm()
        return render(request, 'user/password.html', context={'form': form})
    else:
        # 获取提交的邮箱，发送邮件，通过发送的邮箱连接设置新的密码
        email = request.POST.get('email')
        print('-------------1111',email)
        user = UserProfile.objects.filter(email=email).first()
        request.session['id'] = user.id
        uid = str(uuid.uuid4()).replace('-', '')
        cache.set('uid', email)
        # 给此邮箱地址发送邮件
        # 启动异步
        print('------------------',email,uid)
        result = sendmail.delay(email, uid)
        print('-----------------123',result)
        if result:
            return HttpResponse("邮件发送成功！赶快去邮箱更改密码！< a href='/'>返回首页>>> </a>")

#定义一个路由验证验证码
def valide_code(request):
    if request.is_ajax():
        key=request.GET.get('key')
        code=request.GET.get('code')
        captche=CaptchaStore.objects.filter(hashkey=key).first()
        if captche.response==code.lower():
            #正确
            data={'status':1}
        else:
            #错误
            data={'status':0}
        return JsonResponse(data)

#更改密码
def update_pwd(request):
    if request.method=='GET':
        c=request.GET.get('c')
        request.session['c'] = c   #后续个人中心-修改密码使用
        return render(request,'user/update_pwd.html',context={'c':c})
    else:
        code=request.POST.get('code')
        if code:   #忘记密码-修改密码
            uid=request.session.get(code)
            user=UserProfile.objects.get(pk=uid)
        else:    #用户已登录---修改密码
            user = UserProfile.objects.get(pk=request.user.id)
        #获取密码
        old_pwd=request.POST.get('old_password') #旧密码
        pwd=request.POST.get('password1')  #新密码
        repwd=request.POST.get('password2')  #确认密码
        if pwd==repwd and user and check_password(old_pwd,user.password):
            pwd=make_password(pwd)
            user.password=pwd
            user.save()
            return render(request,'user/login.html',context={'msg':'用户密码更新成功！'})
        else:
            return render(request, 'user/update_pwd.html', context={'msg': '更新失败！'})

#注销
def user_logout(request):
    request.session.flush()  # 删除django_session+cookie+字典
    logout(request)  # 系统自带的注销
    return redirect(reverse('index'))

#个人中心-修改
def personal(request):
    user1 = UserProfile.objects.get(pk=request.user.id)
    return render(request,'user/personal.html',context={'user1':user1})

#发送验证码
#发送验证码  ajax发过来的请求
def send_code(request):
    mobile=request.GET.get('mobile')
    data = {}
    if UserProfile.objects.filter(mobile=mobile).exists():
        #发送验证码
        json_result=util_sendmsg(mobile)
        #取值：
        status=json_result.get('code')
        if status==200:
            check_code=json_result.get('obj')
            #使用session保存   获取到的手机验证码保存到session中
            request.session[mobile]=check_code
            print(check_code,'--------------check')

            data['status'] = 200
            data['msg'] = '验证码发送成功'
        else:
            data['status']=500
            data['msg']='验证码发送失败'
    else:
        data['status']=501
        data['msg']='用户不存在'
    print('----------1212')
    return JsonResponse(data)

#手机验证码登录
def code_login(request):
    if request.method=='GET':
        return render(request,'user/codelogin.html')
    # else:
    #     mobile=request.POST.get('mobile')   #页面传的手机号
    #     code=request.POST.get('code')   #页面输入的验证码
    #     #根据mobile去session中取值
    #     check_code=request.session.get(mobile)
    #     print('-----------------111', mobile, code,check_code)
    #     if code==check_code:
    #         print('----------',)
    #         user=UserProfile.objects.filter(mobile=mobile).first()
    #         # user=authenticate(username=user.username,password=user.password)
    #         if user:
    #             login(request,user)
    #         return redirect(reverse('index'))
    #     else:
    #         return render(request,'user/codelogin.html',context={'msg':'验证码有误！'})






