from django.urls import path
from .views import check_review_api, get_result, task_status
from reviews.views import show_ozon_reviews

urlpatterns = [
    path('check/', check_review_api, name='check-review'),
    path('results/<uuid:result_id>/', get_result, name='get-result'),
    path('results/<int:result_id>/', get_result),
    path('task-status/<str:task_id>/', task_status, name='task-status'),
    path('ozon_reviews/', show_ozon_reviews, name='ozon-reviews'),
]