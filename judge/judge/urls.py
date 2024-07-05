from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("judgement.urls")),
    path("admin/", admin.site.urls),
]
