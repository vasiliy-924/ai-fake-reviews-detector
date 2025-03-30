from django.urls import path
from .views import check_review_api, get_result, task_status

urlpatterns = [
    path('check/', check_review_api, name='check-review'),
    path('results/<uuid:result_id>/', get_result, name='get-result'),
    path('task-status/<str:task_id>/', task_status, name='task-status'),
]