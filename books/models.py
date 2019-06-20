
from django.db import models

# Create your models here.
from user.models import UserProfile


class Book(models.Model):
    title = models.CharField(max_length=50, null=True,blank=True ,verbose_name='书名')
    author = models.CharField(max_length=300, default="未名",verbose_name='作者')
    binding = models.CharField(max_length=20,null=True,blank=True ,verbose_name='精装')
    publisher = models.CharField(max_length=50,verbose_name='出版社')
    pubdate=models.CharField(max_length=50,default='1900-01',verbose_name='出版年')
    price = models.FloatField(verbose_name='定价')
    pages = models.IntegerField(verbose_name='页数')
    isbn = models.CharField(max_length=15, null=True,blank=True ,unique=True,verbose_name='isbn')
    summary = models.CharField(max_length=1000,verbose_name='内容简介')
    image = models.ImageField(upload_to='uploads/book/%Y/%m',verbose_name='书籍图片')
    date = models.DateTimeField(auto_now=True, verbose_name='添加日期')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'book'
        verbose_name = '书籍表'
        verbose_name_plural = verbose_name

class Gift(models.Model):
    uid = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, verbose_name='赠送者', related_name='gift_user')
    bookid=models.ForeignKey(to=Book, on_delete=models.CASCADE, verbose_name='书籍', related_name='gift_book')
    # 是否已经赠送出去
    launched = models.IntegerField(default=0,verbose_name='状态')
    date = models.DateTimeField(auto_now=True, verbose_name='添加日期')

    # def __str__(self):
    #     return self.uid

    class Meta:
        db_table = 'gift'
        verbose_name = '赠送清单'
        verbose_name_plural = verbose_name

class Wish(models.Model):
    uid = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, verbose_name='心愿者', related_name='wish_id')
    bookid=models.ForeignKey(to=Book, on_delete=models.CASCADE, verbose_name='书籍', related_name='wish_book')
    # 是否已经赠送出去
    launched = models.IntegerField(default=0,verbose_name='状态')
    date = models.DateTimeField(auto_now=True, verbose_name='添加日期')

    # def __str__(self):
    #     return self.uid

    class Meta:
        db_table = 'wish'
        verbose_name = '心愿清单'
        verbose_name_plural = verbose_name

class Drift(models.Model):
    # 邮寄信息
    recipient_name = models.CharField(max_length=20, null=False,blank=False,verbose_name='收件人')
    address = models.CharField(max_length=100, null=False,blank=False,verbose_name='书籍收件地址')
    message = models.CharField(max_length=200,verbose_name='留言')
    mobile = models.CharField(max_length=20, null=False,blank=False,verbose_name='联系电话')
    # 书籍信息
    isbn = models.CharField(max_length=13,verbose_name='isbn')
    book_title = models.CharField(max_length=50,verbose_name='书名')
    book_author = models.CharField(max_length=30,verbose_name='作者')
    book_img = models.ImageField(upload_to='uploads/book/%Y/%m',verbose_name='书籍图片')
    # 请求者信息
    requester_id = models.IntegerField(default=0,verbose_name='请求者id')
    requester_nickname = models.CharField(max_length=20,verbose_name='请求者昵称')
    # 赠送者信息
    gifter_id = models.IntegerField(default=0,verbose_name='赠送者id')
    gift_id = models.IntegerField(default=0,verbose_name='赠送清单id')
    gifter_nickname = models.CharField(max_length=20,verbose_name='赠送者昵称')
    # 状态
    status= models.IntegerField(default=1,verbose_name='状态')
    date = models.DateTimeField(auto_now=True, verbose_name='添加日期')

    def __str__(self):
        return self.recipient_name

    class Meta:
        db_table = 'drift'
        verbose_name = '鱼漂'
        verbose_name_plural = verbose_name


