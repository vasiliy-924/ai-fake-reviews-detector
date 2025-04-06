# fake_reviews_detector/create_superuser.py
import os

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username=os.getenv(
        "DJANGO_SUPERUSER_USERNAME")).exists():
    User.objects.create_superuser(
        os.getenv("DJANGO_SUPERUSER_USERNAME"),
        os.getenv("DJANGO_SUPERUSER_EMAIL"),
        os.getenv("DJANGO_SUPERUSER_PASSWORD"),
    )
