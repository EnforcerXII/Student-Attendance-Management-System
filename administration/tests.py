from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from .models import Student, Faculty, Subject, Enrolment


User = get_user_model()


class StudentModelTest(TestCase):
    def test_student_creation(self):
        user = User.objects.create_user(
            username="teststudent",
            password="TestPassword123!",
            role=User.Role.STUDENT,
        )

        student = Student.objects.create(
            student_id="TEST001",
            user=user,
            department="Computer Science",
            year_of_study=2,
        )

        self.assertEqual(student.student_id, "TEST001")
        self.assertEqual(student.user.username, "teststudent")
        self.assertEqual(student.department, "Computer Science")
        self.assertEqual(student.year_of_study, 2)


class EnrolmentConstraintTest(TestCase):
    def test_duplicate_student_subject_enrolment_is_rejected(self):
        # Create a student user
        user = User.objects.create_user(
            username="enrolmentstudent",
            password="TestPassword123!",
            role=User.Role.STUDENT,
        )

        # Create a faculty user
        faculty_user = User.objects.create_user(
            username="enrolmentfaculty",
            password="TestPassword123!",
            role=User.Role.FACULTY,
        )

        # Create the student profile
        student = Student.objects.create(
            student_id="ENR001",
            user=user,
            department="Computer Science",
            year_of_study=2,
        )

        # Create the faculty profile
        faculty = Faculty.objects.create(
            faculty_id="ENRFAC001",
            user=faculty_user,
            department="Computer Science",
        )

        # Create the subject
        subject = Subject.objects.create(
            subject_code="ENRCS101",
            subject_name="Test Enrolment Subject",
            faculty=faculty,
        )

        # Create the first enrolment
        Enrolment.objects.create(
            student=student,
            subject=subject,
        )

        # Verify that a duplicate enrolment is rejected
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Enrolment.objects.create(
                    student=student,
                    subject=subject,
                )