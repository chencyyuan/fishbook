from django.urls import path

from user.views import *

app_name='user'
urlpatterns = [
    path('register',user_register,name='register'),
    path('login',user_login,name='login'),
    path('forget_pwd',forget_password,name='forget_pwd'),
    path('valide_code',valide_code,name='valide_code'),
    path('logout',user_logout,name='logout'),
    path('update_pwd',update_pwd,name='update_pwd'),
    path('personal',personal,name='personal'),
    path('sendcode',send_code,name='sendcode'),
    path('codelogin',code_login,name='codelogin'),
]