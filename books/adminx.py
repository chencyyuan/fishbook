

import xadmin
from books.models import Book, Gift, Wish, Drift


class BookAdmin(object):
    list_display=['title','author','publisher','pubdate','price','pages','isbn'] #页面中显示的列
    search_fields=['isbn','title'] #检索框
    list_editable=['author','publisher','price','pages']  #可编辑列数据
    list_filter=['title','price']  #过滤

class DriftAdmin(object):
    list_display = ['recipient_name', 'address', 'message', 'mobile', 'isbn', 'book_title', 'book_author','requester_nickname','gifter_nickname','date']  # 页面中显示的列

class GiftAdmin(object):
    list_display = ('uid','bookid','launched','date')

class WishAdmin(object):
    list_display = ('uid','bookid','launched','date')

#注册
xadmin.site.register(Book,BookAdmin)
xadmin.site.register(Gift,GiftAdmin)
xadmin.site.register(Wish,WishAdmin)
xadmin.site.register(Drift,DriftAdmin)



