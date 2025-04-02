from django.urls import path
from .views import check_review_api, get_result, task_status
from reviews.views import fetch_otzovik_reviews_view

urlpatterns = [
    path('check/', check_review_api, name='check-review'),
    path('results/<uuid:result_id>/', get_result, name='get-result'),
    path('results/<int:result_id>/', get_result),
    path('task-status/<str:task_id>/', task_status, name='task-status'),
    path('otzovik_reviews/', fetch_otzovik_reviews_view, name='otzovik-reviews'),
]