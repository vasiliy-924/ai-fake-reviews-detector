from django.urls import path
from .views import check_review_api

urlpatterns = [
    path('check/', check_review_api, name='check-review'),
]