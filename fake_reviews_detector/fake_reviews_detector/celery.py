import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fake_reviews_detector.settings')

app = Celery('fake_reviews_detector')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
