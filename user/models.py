from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class UserProfile(AbstractUser):
    mobile = models.CharField(max_length=11, verbose_name='手机号码', unique=True,default='10000000001')
    confirmed = models.BooleanField(default=False,verbose_name='验证')
    beans = models.FloatField(default=0,verbose_name='鱼豆')
    send_counter = models.IntegerField(default=0,verbose_name='送出')
    receive_counter = models.IntegerField(default=0,verbose_name='收到')
    wx_open_id = models.CharField(max_length=50)
    wx_name = models.CharField(max_length=32)

    def __str__(self):
        return self.username

    class Meta:
        db_table='userprofile'
        verbose_name='用户表'
        verbose_name_plural=verbose_name



