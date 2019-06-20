from __future__ import absolute_import, unicode_literals

'''
absolute_import 这个没有搞懂，如果我当前目录有一个sys.py，我用的时候总是会调用系统的sys。如果当前目录和sys.path的路径中都有一个foo，则都会调用当前目录下的foo。
unicode_literals 这个是对字符串使用unicode字符
'''
from .celery import app as celery_app