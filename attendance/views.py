from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from administration.models import Subject
from .models import AttendanceSession

from django.db import transaction
from django.http import HttpResponse
from administration.models import Enrolment
from .models import Attendance
from django.db.models import Count, Q


@login_required
def create_attendance_session(request, subject_id):
    if request.user.role != "FACULTY":
        raise PermissionDenied

    subject = get_object_or_404(
        Subject,
        id=subject_id,
        faculty__user=request.user,
    )

    if request.method == "POST":
        session_date = request.POST.get("session_date")

        if not session_date:
            messages.error(request, "Please select an attendance date.")
        else:
            session, created = AttendanceSession.objects.get_or_create(
                subject=subject,
                session_date=session_date,
                defaults={"created_by": request.user},
            )

            if created:
                messages.success(
                    request,
                    "Attendance session created successfully.",
                )
            else:
                messages.info(
                    request,
                    "An attendance session already exists for this subject and date.",
                )

            return redirect(
                "create_attendance_session",
                subject_id=subject.id,
            )

    context = {
        "subject": subject,
        "sessions": AttendanceSession.objects.filter(subject=subject),
    }

    return render(
        request,
        "attendance/create_session.html",
        context,
    )


@login_required
def mark_attendance(request, session_id):
    if request.user.role != "FACULTY":
        raise PermissionDenied

    session = get_object_or_404(
        AttendanceSession.objects.select_related("subject__faculty__user"),
        id=session_id,
        subject__faculty__user=request.user,
    )

    enrolments = Enrolment.objects.filter(
        subject=session.subject
    ).select_related("student__user")

    students = [enrolment.student for enrolment in enrolments]

    if request.method == "POST":
        valid_statuses = {choice[0] for choice in Attendance.Status.choices}

        with transaction.atomic():
            for student in students:
                status = request.POST.get(f"status_{student.id}")

                if status not in valid_statuses:
                    return HttpResponse(
                        "Invalid attendance status submitted.",
                        status=400,
                    )

                Attendance.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={
                        "status": status,
                        "marked_by": request.user,
                    },
                )

        messages.success(request, "Attendance saved successfully.")
        return redirect("mark_attendance", session_id=session.id)

    existing_attendance = {
        record.student_id: record.status
        for record in Attendance.objects.filter(session=session)
    }

    student_rows = []

    for student in students:
        student_rows.append({
            "student": student,
            "current_status": existing_attendance.get(
                student.id, Attendance.Status.ABSENT
            ),
        })

    context = {
        "session": session,
        "student_rows": student_rows,
        "statuses": Attendance.Status.choices,
    }

    return render(request, "attendance/mark_attendance.html", context)


@login_required
def attendance_report(request, session_id):
    if request.user.role != "FACULTY":
        raise PermissionDenied

    session = get_object_or_404(
        AttendanceSession.objects.select_related("subject__faculty__user"),
        id=session_id,
        subject__faculty__user=request.user,
    )

    total_students = Enrolment.objects.filter(
        subject=session.subject
    ).count()

    attendance_records = Attendance.objects.filter(session=session)

    counts = attendance_records.aggregate(
        present=Count("id", filter=Q(status="PRESENT")),
        absent=Count("id", filter=Q(status="ABSENT")),
        late=Count("id", filter=Q(status="LATE")),
    )

    present_count = counts["present"] or 0
    absent_count = counts["absent"] or 0
    late_count = counts["late"] or 0

    attendance_percentage = (
        round((present_count + late_count) / total_students * 100, 2)
        if total_students > 0
        else 0
    )

    context = {
        "session": session,
        "total_students": total_students,
        "present_count": present_count,
        "absent_count": absent_count,
        "late_count": late_count,
        "attendance_percentage": attendance_percentage,
    }

    return render(request, "attendance/attendance_report.html", context)