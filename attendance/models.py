from django.conf import settings
from django.db import models


class AttendanceSession(models.Model):
    subject = models.ForeignKey(
        "administration.Subject",
        on_delete=models.PROTECT,
        related_name="attendance_sessions",
    )
    session_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_attendance_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "session_date"],
                name="unique_subject_attendance_session_date",
            )
        ]
        ordering = ["-session_date"]

    def __str__(self):
        return f"{self.subject} - {self.session_date}"


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "Late"

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    student = models.ForeignKey(
        "administration.Student",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ABSENT,
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="marked_attendance_records",
    )
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "student"],
                name="unique_student_attendance_per_session",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.session} - {self.status}"
