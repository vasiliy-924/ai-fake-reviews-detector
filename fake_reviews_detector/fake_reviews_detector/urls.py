from django.contrib import admin
from django.urls import path

from reviews.views import check_review_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('check/', check_review_view, name='check'),
]
