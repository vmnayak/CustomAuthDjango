import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_prj.settings')

celery_app = Celery('auth_prj')
celery_app.config_from_object('django.conf:settings', namespace='AUTH_CELERY')
celery_app.autodiscover_tasks()
