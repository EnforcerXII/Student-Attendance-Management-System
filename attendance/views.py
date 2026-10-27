from django.contrib import messages
import csv
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from administration.models import Enrolment, Student, Subject
from .models import Attendance, AttendanceSession
from .services import (
    LOW_ATTENDANCE_THRESHOLD,
    calculate_percentage,
    log_audit_event,
    low_attendance_students,
    student_overall_summary,
    subject_attendance_summary,
)


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
                log_audit_event(
                    user=request.user,
                    action="SESSION_CREATED",
                    entity="AttendanceSession",
                    entity_id=session.id,
                    new_value=str(session.session_date),
                )
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
        existing_records = {
            record.student_id: record
            for record in Attendance.objects.filter(session=session)
        }
        modification_reason = request.POST.get("reason", "").strip()

        with transaction.atomic():
            for student in students:
                status = request.POST.get(f"status_{student.id}")

                if status not in valid_statuses:
                    return HttpResponse(
                        "Invalid attendance status submitted.",
                        status=400,
                    )

                existing_record = existing_records.get(student.id)
                if existing_record:
                    if existing_record.status != status:
                        old_status = existing_record.status
                        existing_record.status = status
                        existing_record.marked_by = request.user
                        existing_record.save()
                        log_audit_event(
                            user=request.user,
                            action="ATTENDANCE_MODIFIED",
                            entity="Attendance",
                            entity_id=existing_record.id,
                            old_value=old_status,
                            new_value=status,
                            reason=modification_reason or "Faculty modification",
                        )
                else:
                    new_record = Attendance.objects.create(
                        session=session,
                        student=student,
                        status=status,
                        marked_by=request.user,
                    )
                    log_audit_event(
                        user=request.user,
                        action="ATTENDANCE_MARKED",
                        entity="Attendance",
                        entity_id=new_record.id,
                        new_value=status,
                    )

        messages.success(request, "Attendance saved successfully.")
        return redirect("mark_attendance", session_id=session.id)

    existing_attendance = {
        record.student_id: record.status
        for record in Attendance.objects.filter(session=session)
    }

    student_rows = []
    has_existing = bool(existing_attendance)

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
        "is_modifying": has_existing,
    }

    return render(request, "attendance/mark_attendance.html", context)


@login_required
def modify_attendance(request, session_id):
    """Permitted modification of existing attendance records (SAM-F-014, TC-ATT-03)."""
    return mark_attendance(request, session_id)


@login_required
def attendance_report(request, session_id):
    if request.user.role not in ("FACULTY", "ADMIN"):
        raise PermissionDenied

    if request.user.role == "FACULTY":
        session = get_object_or_404(
            AttendanceSession.objects.select_related("subject__faculty__user"),
            id=session_id,
            subject__faculty__user=request.user,
        )
    else:
        session = get_object_or_404(
            AttendanceSession.objects.select_related("subject"),
            id=session_id,
        )

    enrolments = Enrolment.objects.filter(
        subject=session.subject
    ).select_related("student__user")

    total_students = enrolments.count()
    attendance_records = Attendance.objects.filter(session=session).select_related("student__user")

    counts = attendance_records.aggregate(
        present=Count("id", filter=Q(status="PRESENT")),
        absent=Count("id", filter=Q(status="ABSENT")),
        late=Count("id", filter=Q(status="LATE")),
    )

    present_count = counts["present"] or 0
    absent_count = counts["absent"] or 0
    late_count = counts["late"] or 0

    attendance_percentage = calculate_percentage(present_count + late_count, total_students)

    context = {
        "session": session,
        "total_students": total_students,
        "present_count": present_count,
        "absent_count": absent_count,
        "late_count": late_count,
        "attendance_percentage": attendance_percentage,
        "records": attendance_records,
    }

    return render(request, "attendance/attendance_report.html", context)


@login_required
def student_attendance(request):
    """Student view of own attendance and history with alert banner (SAM-F-017, F-023, F-024)."""
    if request.user.role != "STUDENT":
        raise PermissionDenied

    student = get_object_or_404(Student, user=request.user)

    summaries = student_overall_summary(student)
    low_attendance_alerts = [s for s in summaries if s["is_low"]]

    history = (
        Attendance.objects.filter(student=student)
        .select_related("session__subject")
        .order_by("-session__session_date")
    )

    context = {
        "student": student,
        "summaries": summaries,
        "history": history,
        "low_attendance_alerts": low_attendance_alerts,
        "threshold": LOW_ATTENDANCE_THRESHOLD,
    }
    return render(request, "attendance/student_attendance.html", context)


@login_required
def defaulters_list(request, subject_id):
    """View students below minimum attendance threshold (SAM-F-020, TC-CALC-02)."""
    if request.user.role not in ("FACULTY", "ADMIN"):
        raise PermissionDenied

    if request.user.role == "FACULTY":
        subject = get_object_or_404(
            Subject,
            id=subject_id,
            faculty__user=request.user,
        )
    else:
        subject = get_object_or_404(Subject, id=subject_id)

    try:
        threshold = float(request.GET.get("threshold", LOW_ATTENDANCE_THRESHOLD))
    except (ValueError, TypeError):
        threshold = LOW_ATTENDANCE_THRESHOLD

    summary = subject_attendance_summary(subject, threshold)

    context = {
        "subject": subject,
        "threshold": threshold,
        "summary": summary,
        "defaulters": summary["defaulters"],
    }
    return render(request, "attendance/defaulters_list.html", context)


@login_required
def reports_dashboard(request):
    """Comprehensive attendance reports and statistics with CSV export (SAM-F-021, F-022, TC-REP-01, TC-REP-02)."""
    if request.user.role not in ("FACULTY", "ADMIN"):
        raise PermissionDenied

    if request.user.role == "FACULTY":
        subjects = Subject.objects.filter(faculty__user=request.user)
    else:
        subjects = Subject.objects.all()

    selected_subject_id = request.GET.get("subject")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    student_query = request.GET.get("student", "").strip()

    records = Attendance.objects.filter(
        session__subject__in=subjects
    ).select_related("session__subject", "student__user", "session", "marked_by")

    selected_subject = None
    if selected_subject_id:
        records = records.filter(session__subject_id=selected_subject_id)
        selected_subject = subjects.filter(id=selected_subject_id).first()

    if start_date:
        records = records.filter(session__session_date__gte=start_date)
    if end_date:
        records = records.filter(session__session_date__lte=end_date)
    if student_query:
        records = records.filter(
            Q(student__student_id__icontains=student_query)
            | Q(student__user__first_name__icontains=student_query)
            | Q(student__user__last_name__icontains=student_query)
            | Q(student__user__username__icontains=student_query)
        )

    records = records.order_by("-session__session_date")

    # CSV Export
    if request.GET.get("format") == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="attendance_report.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "Student ID",
            "Student Name",
            "Subject Code",
            "Subject Name",
            "Date",
            "Status",
            "Marked By",
        ])
        for record in records:
            writer.writerow([
                record.student.student_id,
                record.student.user.get_full_name() or record.student.user.username,
                record.session.subject.subject_code,
                record.session.subject.subject_name,
                record.session.session_date,
                record.status,
                record.marked_by.username if record.marked_by else "",
            ])
        return response

    counts = records.aggregate(
        total=Count("id"),
        present=Count("id", filter=Q(status="PRESENT")),
        late=Count("id", filter=Q(status="LATE")),
        absent=Count("id", filter=Q(status="ABSENT")),
    )
    total = counts["total"] or 0
    present = counts["present"] or 0
    late = counts["late"] or 0
    absent = counts["absent"] or 0
    percentage = calculate_percentage(present + late, total)

    context = {
        "subjects": subjects,
        "selected_subject": selected_subject,
        "selected_subject_id": selected_subject_id,
        "start_date": start_date or "",
        "end_date": end_date or "",
        "student_query": student_query,
        "records": records[:200],  # Limit to 200 for fast page rendering
        "total_records": total,
        "present_count": present,
        "late_count": late,
        "absent_count": absent,
        "overall_percentage": percentage,
    }
    return render(request, "attendance/reports_dashboard.html", context)
