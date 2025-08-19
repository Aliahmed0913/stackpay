from celery import Celery
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE','Restaurant.settings')

app = Celery('Restaurant')

app.config_from_object('django.conf:settings',namespace='CELERY_')

app.autodiscover_tasks()