from django.conf import settings
from django.db import models


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    department = models.CharField(max_length=100, blank=True)
    year_of_study = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"


class Faculty(models.Model):
    faculty_id = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="faculty_profile",
    )
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name() or self.user.username}"


class Subject(models.Model):
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=150)
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.PROTECT,
        related_name="subjects",
    )

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


class Enrolment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrolments",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="enrolments",
    )
    enrolled_on = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject"],
                name="unique_student_subject_enrolment",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.subject}"
