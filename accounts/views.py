from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.shortcuts import redirect

from administration.models import Subject, Student, Enrolment
from attendance.models import Attendance


@login_required
def dashboard(request):
    user_role = request.user.role

    context = {
        "username": request.user.username,
        "user_role": user_role,
    }

    if user_role == "ADMIN":
        context["dashboard_title"] = "Admin Dashboard"

        from administration.models import Faculty
        from attendance.models import AttendanceSession

        context["total_students"] = Student.objects.count()
        context["total_faculty"] = Faculty.objects.count()
        context["total_subjects"] = Subject.objects.count()
        context["total_sessions"] = AttendanceSession.objects.count()

    elif user_role == "FACULTY":
        context["dashboard_title"] = "Faculty Dashboard"

    else:
        context["dashboard_title"] = "Student Dashboard"

        try:
            student = Student.objects.get(user=request.user)

            attendance_records = Attendance.objects.filter(
                student=student
            ).select_related("session__subject").order_by(
                "-session__session_date"
            )

            total_classes = attendance_records.count()

            present_count = attendance_records.filter(
                status="PRESENT"
            ).count()

            late_count = attendance_records.filter(
                status="LATE"
            ).count()

            attended_count = present_count + late_count

            attendance_percentage = (
                round(attended_count / total_classes * 100, 2)
                if total_classes > 0
                else 0
            )

            context.update({
                "attendance_records": attendance_records,
                "total_classes": total_classes,
                "present_count": present_count,
                "late_count": late_count,
                "attendance_percentage": attendance_percentage,
            })

        except Student.DoesNotExist:
            context.update({
                "attendance_records": [],
                "total_classes": 0,
                "present_count": 0,
                "late_count": 0,
                "attendance_percentage": 0,
            })

    return render(request, "dashboard.html", context)


@login_required
def faculty_dashboard(request):
    if request.user.role != "FACULTY":
        raise PermissionDenied

    subjects = Subject.objects.filter(faculty__user=request.user)

    context = {
        "subjects": subjects,
        "username": request.user.username,
    }

    return render(request, "faculty_dashboard.html", context)

@login_required
def role_redirect(request):
    if request.user.role == "FACULTY":
        return redirect("faculty_dashboard")

    return redirect("dashboard")