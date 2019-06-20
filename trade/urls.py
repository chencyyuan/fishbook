from django.urls import path

from trade.views import *

app_name='trade'
urlpatterns = [
    path('order', order, name='order'), #订单

    path('alipay', alipay, name='alipay'), #支付
    path('checkpay', check_pay, name='checkpay'), #验证支付
]