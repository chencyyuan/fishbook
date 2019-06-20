import uuid

from alipay import AliPay
from django.core.mail import send_mail
from fishbook.settings import EMAIL_HOST_USER, PRIVATE_KEY_PATH, PUBLIC_KEY_PATH


#发送邮件 gift
def send_email(email,request,user,title):
    subject='[鱼书] 有人想要一本书'
    ran_code=uuid.uuid4()
    ran_code=str(ran_code)
    ran_code=ran_code.replace('-','')
    request.session[ran_code]=user.id
    message='''
    <p><stong>亲爱的 %s ,</stong></p>
    <p>%s 想要一本《%s》.你刚好有这本书在鱼书上等待赠送。</p>
    <p>点击<a
            href="http://127.0.0.1:8000/book/pending">这里</a>查看书籍的邮寄地址.
    </p>
    <p>无论您是否愿意赠送 %s 这本书，都烦请您前往【鱼书】处理此请求。</p>
    <p>如果无法点击，你也可以将下面的地址复制到浏览器中打开:</p>
    <p>http://127.0.0.1:8000/book/pending</p>
    <p>你的，鱼书</p>
    <p>
        <small>注意，请不要回复此邮件哦</small>
    </p>
    '''%(user.username,request.user.username,title,request.user.username)
    result=send_mail(subject,"",EMAIL_HOST_USER,[email,],html_message=message)
    return result

#发送邮件 wish
def send_email1(email,request,user,title,giftid):
    subject='[鱼书] 有人赠送你一本书'
    ran_code=uuid.uuid4()
    ran_code=str(ran_code)
    ran_code=ran_code.replace('-','')
    request.session[ran_code]=user.id
    message='''
    <p><stong>亲爱的 %s,</stong></p>
    <p>%s 有一本《 %s 》可以赠送给你</p>
    <p>点击<a
            href="http://127.0.0.1:8000/book/senddrif1?gid=%s">这里</a>填写书籍邮寄地址，
        等待 %s 将书籍寄送给你
    </p>
    <p>如果无法点击，你也可以将下面的地址复制到浏览器中打开:</p>
    <p>http://127.0.0.1:8000/book/senddrif1?gid=%s</p>
    <p>你的，</p>
    <p>鱼书</p>
    <p>
        <small>注意，请不要回复此邮件哦</small>
    </p>
    '''%(user.username,request.user.username,title,giftid,request.user.username,giftid)
    result=send_mail(subject,"",EMAIL_HOST_USER,[email,],html_message=message)
    return result

