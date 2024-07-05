from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("problem/<int:problem_id>", views.problem, name="problem")
]
