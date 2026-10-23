from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.shortcuts import redirect

from administration.models import Subject


@login_required
def dashboard(request):
    user_role = request.user.role

    if user_role == "ADMIN":
        dashboard_title = "Admin Dashboard"
    elif user_role == "FACULTY":
        dashboard_title = "Faculty Dashboard"
    else:
        dashboard_title = "Student Dashboard"

    context = {
        "dashboard_title": dashboard_title,
        "username": request.user.username,
        "user_role": user_role,
    }

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