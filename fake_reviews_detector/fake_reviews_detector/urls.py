from django.contrib import admin
from django.urls import path, include

from reviews.views import check_review_view, ParseTriggerFormView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('check/', check_review_view, name='check'),
    path('parse/', ParseTriggerFormView.as_view(), name='parse-trigger'),
]
