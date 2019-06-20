from django.urls import path

from books.views import *

app_name = 'book'

urlpatterns = [
    path('mygift', my_gift, name='mygift'),  # 赠送清单
    path('mywish', my_wish, name='mywish'),  # 心愿清单
    path('pending', pending, name='pending'),  # 鱼漂
    path('bookdetail', book_detail, name='bookdetail'),  # 详情
    path('savewish', save_to_wish, name='savewish'),  # 添加心愿
    path('savegift', save_to_gift, name='savegift'),  # 添加赠送
    path('cancelgift', cancel_gift, name='cancelgift'),  # 撤销赠送
    path('cancelwish', cancel_wish, name='cancelwish'),  # 撤销心愿
    path('senddrif', send_drif, name='senddrif'),  # 请求书籍
    path('satisifywish', satisify_wish, name='satisifywish'),  # 赠送书籍
    path('canceldrif', cancel_drif, name='canceldrif'),  # 撤销请求
    path('senddrif1', send_drif1, name='senddrif1'),  # 回复赠送邮件
    path('mailedrift', maile_drift, name='mailedrift'),  # 已邮寄
    path('rejectdrift', reject_drift, name='rejectdrift'),  # 拒绝
]
