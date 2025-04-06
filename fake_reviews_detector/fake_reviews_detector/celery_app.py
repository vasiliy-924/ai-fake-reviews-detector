# fake_reviews_detector/fake_reviews_detector/celery_app.py
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "fake_reviews_detector.settings")

app = Celery("fake_reviews_detector")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.update(
    broker_connection_retry_on_startup=True,  # Решение предупреждения
    worker_redirect_stdouts=False,
)

app.conf.beat_schedule = {
    "parse-otzovik-daily": {
        "task": "api.tasks.parse_and_save_otzovik_reviews",  # Путь к задаче
        "schedule": crontab(hour=3, minute=0),  # Каждый день в 3:00
        "args": (
            "https://otzovik.com/reviews/film_nastupit_leto_2024",
        ),  # URL для парсинга
    },
}
