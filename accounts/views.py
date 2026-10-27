from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from administration.models import Enrolment, Student, Subject
from attendance.models import Attendance, AttendanceSession, AuditLog
from attendance.services import (
    LOW_ATTENDANCE_THRESHOLD,
    student_overall_summary,
    subject_attendance_summary,
)


@login_required
def dashboard(request):
    user_role = request.user.role

    context = {
        "username": request.user.username,
        "user_role": user_role,
        "threshold": LOW_ATTENDANCE_THRESHOLD,
    }

    if user_role == "ADMIN":
        context["dashboard_title"] = "Admin Dashboard"

        from administration.models import Faculty

        context["total_students"] = Student.objects.count()
        context["total_faculty"] = Faculty.objects.count()
        context["total_subjects"] = Subject.objects.count()
        context["total_sessions"] = AttendanceSession.objects.count()
        context["total_records"] = Attendance.objects.count()
        context["total_audit_logs"] = AuditLog.objects.count()

    elif user_role == "FACULTY":
        context["dashboard_title"] = "Faculty Dashboard"
        assigned_subjects = Subject.objects.filter(faculty__user=request.user)
        context["assigned_subjects_count"] = assigned_subjects.count()
        context["total_sessions"] = AttendanceSession.objects.filter(
            subject__in=assigned_subjects
        ).count()

    else:
        context["dashboard_title"] = "Student Dashboard"

        try:
            student = Student.objects.get(user=request.user)
            summaries = student_overall_summary(student)
            low_attendance_alerts = [s for s in summaries if s["is_low"]]

            attendance_records = (
                Attendance.objects.filter(student=student)
                .select_related("session__subject")
                .order_by("-session__session_date")
            )

            total_classes = attendance_records.count()
            present_count = attendance_records.filter(status="PRESENT").count()
            late_count = attendance_records.filter(status="LATE").count()
            attended_count = present_count + late_count

            attendance_percentage = (
                round(attended_count / total_classes * 100, 2)
                if total_classes > 0
                else 0
            )

            context.update({
                "student": student,
                "summaries": summaries,
                "low_attendance_alerts": low_attendance_alerts,
                "attendance_records": attendance_records,
                "total_classes": total_classes,
                "present_count": present_count,
                "late_count": late_count,
                "attendance_percentage": attendance_percentage,
            })

        except Student.DoesNotExist:
            context.update({
                "student": None,
                "summaries": [],
                "low_attendance_alerts": [],
                "attendance_records": [],
                "total_classes": 0,
                "present_count": 0,
                "late_count": 0,
                "attendance_percentage": 0,
            })

    return render(request, "dashboard.html", context)


@login_required
def faculty_dashboard(request):
    """Faculty view of assigned classes with stats and actions (SAM-F-019, TC-VIEW-02)."""
    if request.user.role != "FACULTY":
        raise PermissionDenied

    subjects = Subject.objects.filter(faculty__user=request.user)
    subject_cards = []

    for subject in subjects:
        summary = subject_attendance_summary(subject)
        subject_cards.append({
            "subject": subject,
            "summary": summary,
        })

    context = {
        "subjects": subjects,
        "subject_cards": subject_cards,
        "username": request.user.username,
        "threshold": LOW_ATTENDANCE_THRESHOLD,
    }

    return render(request, "faculty_dashboard.html", context)


@login_required
def role_redirect(request):
    if request.user.role == "FACULTY":
        return redirect("faculty_dashboard")

    return redirect("dashboard")