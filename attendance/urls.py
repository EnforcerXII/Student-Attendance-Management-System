from django.urls import path
from . import views

urlpatterns = [
    path(
        "subject/<int:subject_id>/sessions/",
        views.create_attendance_session,
        name="create_attendance_session",
    ),

    path(
        "sessions/<int:session_id>/mark/",
        views.mark_attendance,
        name="mark_attendance",
    ),

    path(
        "report/<int:session_id>/",
        views.attendance_report,
        name="attendance_report",
    ),
]