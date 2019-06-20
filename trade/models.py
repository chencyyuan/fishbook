from django.db import models

# Create your models here.
#充值鱼豆
from user.models import UserProfile


class OrderInfo(models.Model):
    """
    订单
    """

    user = models.ForeignKey(to=UserProfile, verbose_name="用户", on_delete=models.CASCADE)
    order_sn = models.CharField(max_length=30, null=True, blank=True, unique=True, verbose_name="订单号")
    trade_no = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name=u"交易号")
    beans_num = models.IntegerField(default=0, verbose_name="鱼豆数量")
    pay_status = models.CharField(default=0, max_length=30, verbose_name="订单状态")
    order_mount = models.FloatField(default=0.0, verbose_name="订单金额")
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")
    add_time = models.DateTimeField(auto_now=True, verbose_name="添加时间")

    class Meta:
        db_table = 'orderInfo'
        verbose_name = u"订单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.order_sn)
