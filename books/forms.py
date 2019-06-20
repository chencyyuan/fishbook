import re
from django.core.exceptions import ValidationError
from django.forms import Form
from django import forms

from books.models import Drift


class DriftForm(Form):    # 鱼漂表单信息
    recipient_name = forms.CharField(label='收件人姓名', max_length=20,min_length=2,error_messages={'required': '收件人姓名长度必须在2到20个字符之间'})
    mobile = forms.CharField(label='手机号', required=True, error_messages={'required': '必须填写手机号码'})
    message = forms.CharField(label='留言')
    address = forms.CharField(label='邮寄地址', max_length=70,min_length=10,error_messages={'required': '地址还不到10个字吗？尽量写详细一些吧'})

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        result = re.match(r'^1[0-9]{10}$', mobile)
        if not result:
            raise ValidationError('手机号不合法！')
        return mobile

