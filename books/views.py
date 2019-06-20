from alipay import AliPay
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from books.forms import DriftForm
from books.models import Book, Wish, Gift, Drift
from fishbook.settings import PRIVATE_KEY_PATH, PUBLIC_KEY_PATH
from user.models import UserProfile
from books.utils import send_email, send_email1


def index(request):
    q =request.GET.get('q')
    if q:  #模糊搜索
        books = Book.objects.filter(Q(isbn__icontains=q)|Q(title__icontains=q)).order_by('-date')
    else:
        books = Book.objects.all().order_by('-date')

    #分页
    paginator = Paginator(books, 2)  # Paginator(对象列表，每页显示几条)
    # 方法： get_page()
    page = request.GET.get('page', 1)
    page = paginator.get_page(page)  # 返回的是page对象  获取当前(页码)
    page_list = [x for x in range(page.number - 2, page.number + 3) if x in paginator.page_range]
    # 添加省略号
    if page_list[0] - 1 >= 2:  # 判断当前第一个元素减1是否大于2
        page_list.insert(0, "...")  # 则插入该数组成为第一个元素 ...
    if paginator.num_pages - page_list[-1] >= 2:  # 判断最大页码数-最后一个元素相减是否大于2
        page_list.append("...")  # 则添加一个元素

    # 添加首尾页
    if page_list[0] == "...":
        page_list.insert(0, 1)  # 则插入该数组成为第一个元素(首页)
    if page_list[-1] != paginator.num_pages:  # 判断是否不等于最大页码
        page_list.append(paginator.num_pages)  # 不等于则插入到最后一个元素(尾页)

    return render(request, 'index.html',context={'books':books,'page':page,'page_list':page_list})

#赠送清单
@login_required
def my_gift(request):
    gifts=Gift.objects.filter(uid_id=request.user.id).order_by('-date').all().order_by('-date')
    wishall=Wish.objects.raw("select bookid_id id,count(bookid_id) bcount from wish where launched = 0 group by bookid_id")
    return render(request, 'book/my-gifts.html',context={'gifts':gifts,'wishall':wishall})

#添加书籍到赠送清单
def save_to_gift(request):
    if not request.user.id:
        return JsonResponse({'status':2})
    else:
        bid = request.GET.get('bid')
        isgift=Gift.objects.filter(bookid_id=bid,uid_id=request.user.id)
        if not isgift:
            Gift.objects.create(bookid_id=bid,uid_id=request.user.id)
            #添加0.5颗鱼豆
            user=UserProfile.objects.get(pk=request.user.id)
            user.beans += 0.5
            user.save()
        else:
            return JsonResponse({'status': 1})
        return JsonResponse({'status': 0})

#撤销--赠送清单
def cancel_gift(request):
    bid = request.GET.get('bid')
    #删除
    Gift.objects.filter(bookid_id=bid,uid_id=request.user.id).delete()

    #减少0.5鱼豆
    user = UserProfile.objects.get(pk=request.user.id)
    user.beans -= 0.5
    user.save()
    return redirect(reverse('book:mygift'))

#心愿清单
@login_required
def my_wish(request):
    wishs = Wish.objects.filter(uid_id=request.user.id).order_by('-date').all().order_by('-date')
    giftall = Gift.objects.raw(
        "select bookid_id id,count(bookid_id) bcount from gift where launched = 0 group by bookid_id")
    return render(request, 'book/my-wish.html', context={'wishs': wishs,'giftall':giftall})

#添加书籍到心愿清单
# @login_required
def save_to_wish(request):
    if not request.user.id:
        return JsonResponse({'status':2})
    else:
        bid = request.GET.get('bid')
        iswish=Wish.objects.filter(bookid_id=bid,uid_id=request.user.id)
        if not iswish:
            Wish.objects.create(bookid_id=bid,uid_id=request.user.id)
        else:
            return JsonResponse({'status':1})
        return JsonResponse({'status':0})

#撤销--心愿清单
def cancel_wish(request):
    bid = request.GET.get('bid')

    #删除
    Wish.objects.filter(bookid_id=bid,uid_id=request.user.id).delete()
    return redirect(reverse('book:mywish'))

#详情
def book_detail(request):
    id = request.GET.get('id')
    book = Book.objects.get(pk=id)
    #是否添加过赠送清单、心愿清单
    has_in_gifts =int(Gift.objects.filter(bookid_id=id,uid=request.user.id).exists())
    has_in_wishs=int(Wish.objects.filter(bookid_id=id,uid=request.user.id).exists())

    # 赠书人列表和索要人列表
    trade_gifts = Gift.objects.filter(bookid_id=id).exclude(uid=request.user.id).all()
    trade_wishs = Wish.objects.filter(bookid_id=id).exclude(uid=request.user.id).all()

    #统计多少人赠送过此书 、多少人想要此书
    giftcount=Gift.objects.filter(bookid_id=id).count()
    wishcount=Wish.objects.filter(bookid_id=id).count()

    return render(request, 'book/book-detail.html',context={'book':book,'has_in_gifts':has_in_gifts,'has_in_wishs':has_in_wishs,'giftcount':giftcount,'wishcount':wishcount,'trade_gifts':trade_gifts,'trade_wishs':trade_wishs})

#鱼漂
@login_required
def pending(request):
    #查看当前登录用户交易信息
    # drifts=Drift.objects.filter(gifter_id=request.user.id).order_by('-date')
    drifts=Drift.objects.all().order_by('-date')
    return render(request, 'book/pending.html',context={'drifts':drifts})

#请求书籍
@login_required
def send_drif(request):
    gid=request.GET.get('gid')
    gift=Gift.objects.get(pk=gid)
    #当前用户鱼豆少于1颗
    user=UserProfile.objects.get(pk=request.user.id)
    if user.beans < 1.0:
        return render(request,'book/nobeans.html',context={'beans':user.beans})
    #当前用户的鱼豆充足
    form = DriftForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            # 发送邮件给赠书人
            result=send_email(gift.uid.email, request, user, gift.bookid.title)
            if result:
                #保存交易信息
                data=form.cleaned_data
                drift = Drift()
                drift.recipient_name=data.get('recipient_name')
                drift.mobile=data.get('mobile')
                drift.message=data.get('message')
                drift.address=data.get('address')
                drift.gift_id = gift.id
                drift.requester_id = request.user.id
                drift.requester_nickname = request.user.username
                drift.gifter_nickname = gift.uid.username
                drift.gifter_id = gift.uid.id
                drift.book_title = gift.bookid.title
                drift.book_author = gift.bookid.author
                drift.book_img = gift.bookid.image
                drift.isbn = gift.bookid.isbn
                drift.save()

                #改变赠送人gift该数据的状态 1:交易中
                gift.launched = 1
                gift.save()

                # 改变请求人wish该数据的状态 1:交易中
                wish=Wish.objects.filter(uid_id=request.user.id,bookid_id=gift.bookid_id).first()
                wish.launched = 1
                wish.save()

                # 消耗1颗鱼豆
                user = UserProfile.objects.get(pk=request.user.id)
                user.beans -= 1.0
                user.save()

                return redirect(reverse('book:pending'))
        return render(request,'book/drift.html',context={'gift':gift,'userbeans':user.beans,'msg':'提交失败！','errors':form.errors})
    return render(request,'book/drift.html',context={'gift':gift,'userbeans':user.beans})

#赠送书籍
@login_required
def satisify_wish(request):
    wid = request.GET.get('wid')
    print('--------123',wid)
    wish = Wish.objects.get(pk=wid)
    print('-------111',wish)
    # 发送邮件----赠书
    user = UserProfile.objects.get(pk=wish.uid.id)
    gift=Gift.objects.filter(bookid_id=wish.bookid_id,uid_id=request.user.id).first()
    result=send_email1(wish.uid.email, request, user, wish.bookid.title,gift.id)
    print('------',result)
    #邮件发送成功
    if result:
        # 改变心愿人wish该数据的状态
        wish.launched = 1
        wish.save()

        # 改变赠送人wish该数据的状态
        gift.launched = 1
        gift.save()

        # 获得1颗鱼豆
        user = UserProfile.objects.get(pk=wish.uid_id)
        user.beans += 1.0
        user.save()
    return redirect(reverse('book:mygift'))

#回复赠送人的书籍，收到赠送的人不消耗鱼豆
@login_required
def send_drif1(request):
    gid = request.GET.get('gid')
    gift = Gift.objects.get(pk=gid)

    form = DriftForm(request.POST)
    user = UserProfile.objects.get(pk=gift.uid.id)
    if request.method == 'POST' and form.is_valid():
        # 发送邮件给赠书人
        result = send_email(gift.uid.email, request, user, gift.bookid.title)
        if result:
            data = form.cleaned_data
            drift = Drift()
            drift.recipient_name = data.get('recipient_name')
            drift.mobile = data.get('mobile')
            drift.message = data.get('message')
            drift.address = data.get('address')
            drift.gift_id = gift.id
            drift.requester_id = request.user.id
            drift.requester_nickname = request.user.username
            drift.gifter_nickname = gift.uid.username
            drift.gifter_id = gift.uid.id
            drift.book_title = gift.bookid.title
            drift.book_author = gift.bookid.author
            drift.book_img = gift.bookid.image
            drift.isbn = gift.bookid.isbn
            drift.save()

            # 改变gift该数据的状态   交易中
            gift.launched = 1
            gift.save()

            return redirect(reverse('book:pending'))
    return render(request, 'book/drift.html', context={'gift': gift, 'userbeans': user.beans, 'form': form})

#鱼漂--撤销2
def cancel_drif(request):
    did = request.GET.get('did')
    # 修改gift的状态为False
    drift = Drift.objects.get(pk=did)
    gift = Gift.objects.get(pk=drift.gift_id)
    gift.launched = 0
    gift.save()

    # 更改状态为2---你已撤销
    drift.status=2
    drift.save()

    # 增加1颗鱼豆
    user = UserProfile.objects.get(pk=request.user.id)
    user.beans += 1.0
    user.save()
    return redirect(reverse('book:pending'))

#鱼漂---已邮寄3
def maile_drift(request):
    did = request.GET.get('did')
    drift = Drift.objects.get(pk=did)
    # 更改状态为3---已邮寄
    drift.status = 3
    drift.save()

    #已邮寄，请求人的请求数量加1
    quser=UserProfile.objects.get(pk=drift.requester_id)  #请求人
    quser.receive_counter +=1
    quser.save()
    # 赠送人的赠送数量加1
    zuser=UserProfile.objects.get(pk=drift.gifter_id)  #赠送人
    zuser.send_counter +=1
    zuser.save()

    #获取书籍id
    gift=Gift.objects.get(pk=drift.gift_id)
    # 将请求者wish表里的书籍状态改为3：已获得此书
    wish=Wish.objects.filter(uid_id=drift.requester_id,bookid_id=gift.bookid_id).first()
    wish.launched = 3
    print(wish)
    wish.save()
    # 将赠送者gift表里的书籍状态改为3：此书已赠送
    gift.launched = 3
    gift.save()
    return redirect(reverse('book:pending'))

#鱼漂---拒绝4
def reject_drift(request):
    did = request.GET.get('did')
    # 修改gift的状态为False
    drift = Drift.objects.get(pk=did)
    gift = Gift.objects.get(pk=drift.gift_id)
    gift.launched = 0
    gift.save()

    # 修改wish的状态为False
    wish=Wish.objects.filter(uid_id=drift.requester_id,bookid_id=gift.bookid_id).first()
    wish.launched = 0
    wish.save()

    # 更改状态为4---拒绝
    drift.status = 4
    drift.save()
    return redirect(reverse('book:pending'))


