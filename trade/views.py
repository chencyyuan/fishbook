import random
import time

from alipay import AliPay
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.

#购买鱼豆   支付宝
from django.urls import reverse

from fishbook.settings import PRIVATE_KEY_PATH, PUBLIC_KEY_PATH
from trade.models import OrderInfo

from user.models import UserProfile


def order(request):
    beanmoney = request.GET.get('beanmoney', None)
    user1 = UserProfile.objects.get(pk=request.user.id)
    # 创建支付记录
    if beanmoney:
        no = str(int(time.time())) + str(random.randint(100, 999))
        order = OrderInfo.objects.create(order_sn=no, beans_num=(float(beanmoney) * 100.0), order_mount=beanmoney,user_id=request.user.id)
        if order:
            ord = OrderInfo.objects.filter(user_id=request.user.id).order_by('-add_time').first()

            return render(request,'user/personalpay.html',context={'user1':user1,'ord':ord})
    return render(request,'user/personalpay.html',context={'user1':user1})


def alipay(request):
    order_no = request.POST.get("order_no")
    order=OrderInfo.objects.filter(order_sn=order_no).first()
    # 创建用于进行支付宝支付的工具对象
    app_private_key_string = open(PRIVATE_KEY_PATH).read()
    alipay_public_key_string = open(PUBLIC_KEY_PATH).read()

    alipay = AliPay(
        appid="2016093000627747",  # 获取沙箱appid
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order.order_sn,
        total_amount=order.order_mount,
        subject=order.order_sn,
        return_url="http://127.0.0.1:8000/user/personal",
        notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
    )

    url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
    return JsonResponse({"message": "请求支付成功", "url": url})

def check_pay(request):
    order_no = request.GET.get("order_no")
    app_private_key_string = open(PRIVATE_KEY_PATH).read()
    alipay_public_key_string = open(PUBLIC_KEY_PATH).read()
    alipay = AliPay(
        appid="2016093000627747",  # 获取沙箱appid
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    while True:
        # 调用alipay工具查询支付结果
        response = alipay.api_alipay_trade_query(order_no)  # response是一个字典
        # 判断支付结果
        code = response.get("code")  # 支付宝接口调用成功或者错误的标志
        trade_status = response.get("trade_status")  # 用户支付的情况

        if code == "10000" and trade_status == "TRADE_SUCCESS":
            # 表示用户支付成功

            #用户账户的鱼豆增加，order表的状态改变

            # 返回前端json，通知支付成功
            return JsonResponse({"code": 0, "message": "支付成功"})

        elif code == "40004" or (code == "10000" and trade_status == "WAIT_BUYER_PAY"):
            # 表示支付宝接口调用暂时失败，（支付宝的支付订单还未生成） 后者 等待用户支付
            # 继续查询
            print(code)
            print(trade_status)
            continue
        else:
            # 支付失败
            # 返回支付失败的通知
            return JsonResponse({"code": 1, "message": "支付失败"})



