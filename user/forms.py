import re

from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, EmailField
from django import forms

from user.models import UserProfile


class UserRegisterForm(Form):
    username = forms.CharField(max_length=50, min_length=2, error_messages={'min_length': '用户名长度至少2位', }, label='用户名')
    email = forms.EmailField(required=True, error_messages={'required': '必须填写邮箱信息'}, label='邮箱')
    mobile = forms.CharField(required=True, error_messages={'required': '必须填写手机号码'}, label='手机')
    password = forms.CharField(required=True, error_messages={'required': '必须填写密码'}, label='密码',
                               widget=forms.widgets.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        result = re.match(r'[a-zA-Z]\w{1,}', username)
        if not result:
            raise ValidationError('用户名必须字母开头')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        result = re.match(r'^[A-Za-z\d]+([-_.][A-Za-z\d]+)*@([A-Za-z\d]+[-.])+[A-Za-z\d]{2,4}$', email)
        if not result:
            raise ValidationError('email不合法！')
        return email

class RegisterForm(ModelForm):

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password','mobile']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        result = re.match(r'[a-zA-Z]\w{1,}', username)
        if not result:
            raise ValidationError('用户名必须字母开头')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        result = re.match(r'^[A-Za-z\d]+([-_.][A-Za-z\d]+)*@([A-Za-z\d]+[-.])+[A-Za-z\d]{2,4}$', email)
        if not result:
            raise ValidationError('email不合法！')
        return email


class LoginForm(Form):
    email = forms.CharField(max_length=64, min_length=8, error_messages={'min_length': '邮箱长度至少8位','max_length':'邮箱长度至少64位' }, label='邮箱')
    password = forms.CharField(required=True, error_messages={'required': '必须填写密码'}, label='密码',widget=forms.widgets.PasswordInput)
    # class Meta:
    #     model = UserProfile
    #     fields = ['username', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not UserProfile.objects.filter(email=email).exists():
            raise ValidationError('该用户不存在')
        return email

#验证码captcha的From
class CaptchaTestForm(forms.Form):
    email=EmailField(required=True,error_messages='',label='邮箱')
    captcha=CaptchaField(label='验证码')