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
        "sessions/<int:session_id>/modify/",
        views.modify_attendance,
        name="modify_attendance",
    ),
    path(
        "report/<int:session_id>/",
        views.attendance_report,
        name="attendance_report",
    ),
    path(
        "my/",
        views.student_attendance,
        name="student_attendance",
    ),
    path(
        "subject/<int:subject_id>/defaulters/",
        views.defaulters_list,
        name="defaulters_list",
    ),
    path(
        "reports/",
        views.reports_dashboard,
        name="attendance_reports",
    ),
]