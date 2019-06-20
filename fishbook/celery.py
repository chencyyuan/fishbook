import os

from celery import Celery

from fishbook.settings import BROKER_URL, CELERY_RESULT_BACKEND

project_name = os.path.split(os.path.abspath('.'))[-1]

project_settings = '%s.settings' % project_name

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', project_settings)
# 实例化celery
app = Celery(project_name)

# 使用django的配置文件进行配置
app.config_from_object('django.conf:settings')
