from django.contrib import admin
from django.urls import include, path
from reviews.views import ParseTriggerFormView, check_review_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("check/", check_review_view, name="check"),
    path("parse/", ParseTriggerFormView.as_view(), name="parse-trigger"),
]
