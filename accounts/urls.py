from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "faculty/dashboard/",
        views.faculty_dashboard,
        name="faculty_dashboard",
    ),
    path("role-redirect/", views.role_redirect, name="role_redirect"),
]