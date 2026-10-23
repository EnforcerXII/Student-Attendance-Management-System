from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from administration.models import Student, Faculty, Subject, Enrolment
from .models import AttendanceSession, Attendance


User = get_user_model()


class AttendanceModelTest(TestCase):
    def test_attendance_creation(self):
        faculty_user = User.objects.create_user(
            username="testfaculty",
            password="TestPassword123!",
            role=User.Role.FACULTY,
        )

        student_user = User.objects.create_user(
            username="teststudent",
            password="TestPassword123!",
            role=User.Role.STUDENT,
        )

        faculty = Faculty.objects.create(
            faculty_id="FAC_TEST",
            user=faculty_user,
            department="Computer Science",
        )

        student = Student.objects.create(
            student_id="STU_TEST",
            user=student_user,
            department="Computer Science",
            year_of_study=2,
        )

        subject = Subject.objects.create(
            subject_code="CS_TEST",
            subject_name="Test Subject",
            faculty=faculty,
        )

        Enrolment.objects.create(
            student=student,
            subject=subject,
        )

        session = AttendanceSession.objects.create(
            subject=subject,
            session_date=date(2026, 10, 23),
            created_by=faculty_user,
        )

        attendance = Attendance.objects.create(
            session=session,
            student=student,
            status=Attendance.Status.PRESENT,
            marked_by=faculty_user,
        )

        self.assertEqual(attendance.status, Attendance.Status.PRESENT)
        self.assertEqual(attendance.student, student)
        self.assertEqual(attendance.session, session)

    def test_duplicate_attendance_is_rejected(self):
        faculty_user = User.objects.create_user(
            username="duplicatefaculty",
            password="TestPassword123!",
            role=User.Role.FACULTY,
        )

        student_user = User.objects.create_user(
            username="duplicatestudent",
            password="TestPassword123!",
            role=User.Role.STUDENT,
        )

        faculty = Faculty.objects.create(
            faculty_id="DUP_FAC001",
            user=faculty_user,
            department="Computer Science",
        )

        student = Student.objects.create(
            student_id="DUP_STU001",
            user=student_user,
            department="Computer Science",
            year_of_study=2,
        )

        subject = Subject.objects.create(
            subject_code="DUP_CS101",
            subject_name="Duplicate Attendance Test",
            faculty=faculty,
        )

        session = AttendanceSession.objects.create(
            subject=subject,
            session_date=date(2026, 10, 23),
            created_by=faculty_user,
        )

        Attendance.objects.create(
            session=session,
            student=student,
            status=Attendance.Status.PRESENT,
            marked_by=faculty_user,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Attendance.objects.create(
                    session=session,
                    student=student,
                    status=Attendance.Status.ABSENT,
                    marked_by=faculty_user,
                )


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from administration.models import Student, Faculty, Subject, Enrolment
from .models import AttendanceSession, Attendance


class AttendanceWorkflowTests(TestCase):

    def setUp(self):
        User = get_user_model()

        # Create a faculty user
        self.faculty_user = User.objects.create_user(
            username="testfaculty",
            password="testpassword123",
            role="FACULTY",
        )

        # Create the faculty profile
        self.faculty = Faculty.objects.create(
            faculty_id="FAC100",
            user=self.faculty_user,
            department="Computer Science",
        )

        # Create a student user
        self.student_user = User.objects.create_user(
            username="teststudent",
            password="testpassword123",
            role="STUDENT",
        )

        # Create the student profile
        self.student = Student.objects.create(
            student_id="STU100",
            user=self.student_user,
            department="Computer Science",
            year_of_study=2,
        )

        # Create a subject assigned to the faculty
        self.subject = Subject.objects.create(
            subject_code="CS100",
            subject_name="Test Subject",
            faculty=self.faculty,
        )

        # Enrol the student in the subject
        Enrolment.objects.create(
            student=self.student,
            subject=self.subject,
        )

        # Create an attendance session
        self.session = AttendanceSession.objects.create(
            subject=self.subject,
            session_date="2026-10-23",
            created_by=self.faculty_user,
        )

        # Log in as faculty
        self.client.login(
            username="testfaculty",
            password="testpassword123",
        )

    def test_faculty_can_open_attendance_page(self):
        url = reverse(
            "mark_attendance",
            args=[self.session.id],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "STU100")
        self.assertTemplateUsed(
            response,
            "attendance/mark_attendance.html",
        )

    def test_faculty_can_save_attendance(self):
        url = reverse(
            "mark_attendance",
            args=[self.session.id],
        )

        response = self.client.post(
            url,
            {
                f"status_{self.student.id}": "PRESENT",
            },
        )

        self.assertRedirects(response, url)

        record = Attendance.objects.get(
            session=self.session,
            student=self.student,
        )

        self.assertEqual(record.status, "PRESENT")
        self.assertEqual(record.marked_by, self.faculty_user)

    def test_student_cannot_mark_attendance(self):
        self.client.logout()

        self.client.login(
            username="teststudent",
            password="testpassword123",
        )

        url = reverse(
            "mark_attendance",
            args=[self.session.id],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)