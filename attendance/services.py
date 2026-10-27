from django.db.models import Count, Q

from administration.models import Enrolment
from .models import Attendance, AttendanceSession

# Students below this percentage are "low attendance"
LOW_ATTENDANCE_THRESHOLD = 75


def calculate_percentage(attended, total):
    """Return attendance percentage rounded to 2 decimals."""
    if total == 0:
        return 0.0
    return round(attended / total * 100, 2)


def student_subject_summary(student, subject, threshold=LOW_ATTENDANCE_THRESHOLD):
    """Attendance summary of one student in one subject."""
    counts = Attendance.objects.filter(
        student=student,
        session__subject=subject,
    ).aggregate(
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

    return {
        "subject": subject,
        "total": total,
        "present": present,
        "late": late,
        "absent": absent,
        "percentage": percentage,
        "is_low": total > 0 and percentage < threshold,
    }


def student_overall_summary(student, threshold=LOW_ATTENDANCE_THRESHOLD):
    """Summary for every subject the student is enrolled in."""
    enrolments = Enrolment.objects.filter(student=student).select_related("subject")
    return [
        student_subject_summary(student, enrolment.subject, threshold)
        for enrolment in enrolments
    ]


def low_attendance_students(subject, threshold=LOW_ATTENDANCE_THRESHOLD):
    """Students in a subject whose attendance is below the threshold."""
    enrolments = Enrolment.objects.filter(subject=subject).select_related("student__user")
    result = []
    for enrolment in enrolments:
        summary = student_subject_summary(enrolment.student, subject, threshold)
        if summary["is_low"]:
            summary["student"] = enrolment.student
            result.append(summary)
    return result


def subject_attendance_summary(subject, threshold=LOW_ATTENDANCE_THRESHOLD):
    """Aggregate statistics for an entire subject."""
    sessions = AttendanceSession.objects.filter(subject=subject)
    total_sessions = sessions.count()
    enrolments_count = Enrolment.objects.filter(subject=subject).count()

    records = Attendance.objects.filter(session__subject=subject)
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
    defaulters = low_attendance_students(subject, threshold)

    return {
        "subject": subject,
        "total_sessions": total_sessions,
        "enrolled_students": enrolments_count,
        "total_records": total,
        "present": present,
        "late": late,
        "absent": absent,
        "percentage": percentage,
        "defaulters_count": len(defaulters),
        "defaulters": defaulters,
    }


def log_audit_event(user, action, entity, entity_id=None, old_value=None, new_value=None, reason=None):
    """Record an immutable audit log entry (SAM-NF-006, SAM-SR-005)."""
    from .models import AuditLog
    actor = user if (user and hasattr(user, "is_authenticated") and user.is_authenticated) else None
    return AuditLog.objects.create(
        user=actor,
        action=action,
        entity=entity,
        entity_id=str(entity_id) if entity_id is not None else None,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        reason=reason,
    )
