import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lputormis.settings')
app = Celery('lputormis')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

