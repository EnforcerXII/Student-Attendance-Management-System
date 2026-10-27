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


class Sprint2Tests(TestCase):
    """Automated tests for Sprint 2 acceptance criteria and RTM test cases."""

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(
            username="admin_user",
            password="AdminPassword123!",
            role=User.Role.ADMIN,
        )

        self.faculty1_user = User.objects.create_user(
            username="faculty1",
            password="TestPassword123!",
            role=User.Role.FACULTY,
        )
        self.faculty1 = Faculty.objects.create(
            faculty_id="FAC001",
            user=self.faculty1_user,
            department="Computer Science",
        )

        self.faculty2_user = User.objects.create_user(
            username="faculty2",
            password="TestPassword123!",
            role=User.Role.FACULTY,
        )
        self.faculty2 = Faculty.objects.create(
            faculty_id="FAC002",
            user=self.faculty2_user,
            department="Electronics",
        )

        self.student1_user = User.objects.create_user(
            username="student1",
            password="TestPassword123!",
            role=User.Role.STUDENT,
        )
        self.student1 = Student.objects.create(
            student_id="STU001",
            user=self.student1_user,
            department="Computer Science",
            year_of_study=2,
        )

        self.student2_user = User.objects.create_user(
            username="student2",
            password="TestPassword123!",
            role=User.Role.STUDENT,
        )
        self.student2 = Student.objects.create(
            student_id="STU002",
            user=self.student2_user,
            department="Computer Science",
            year_of_study=2,
        )

        # Subjects
        self.subject1 = Subject.objects.create(
            subject_code="CS201",
            subject_name="Data Structures",
            faculty=self.faculty1,
        )
        self.subject2 = Subject.objects.create(
            subject_code="EC201",
            subject_name="Digital Logic",
            faculty=self.faculty2,
        )

        # Enrolments
        Enrolment.objects.create(student=self.student1, subject=self.subject1)
        Enrolment.objects.create(student=self.student2, subject=self.subject1)
        Enrolment.objects.create(student=self.student1, subject=self.subject2)

        # Sessions
        self.session1 = AttendanceSession.objects.create(
            subject=self.subject1,
            session_date=date(2026, 10, 20),
            created_by=self.faculty1_user,
        )
        self.session2 = AttendanceSession.objects.create(
            subject=self.subject1,
            session_date=date(2026, 10, 22),
            created_by=self.faculty1_user,
        )

        # Pre-seed attendance for session 1
        Attendance.objects.create(
            session=self.session1,
            student=self.student1,
            status=Attendance.Status.PRESENT,
            marked_by=self.faculty1_user,
        )
        Attendance.objects.create(
            session=self.session1,
            student=self.student2,
            status=Attendance.Status.ABSENT,
            marked_by=self.faculty1_user,
        )

    def test_tc_att_03_modify_attendance_permitted(self):
        """TC-ATT-03: Permitted edit updates record and writes to AuditLog (SAM-F-014)."""
        self.client.login(username="faculty1", password="TestPassword123!")
        url = reverse("modify_attendance", args=[self.session1.id])

        # Faculty 1 changes Student 2 from ABSENT to PRESENT
        response = self.client.post(
            url,
            {
                f"status_{self.student1.id}": "PRESENT",
                f"status_{self.student2.id}": "PRESENT",
                "reason": "Student attended medical room then rejoined",
            },
        )
        self.assertRedirects(response, reverse("mark_attendance", args=[self.session1.id]))

        record = Attendance.objects.get(session=self.session1, student=self.student2)
        self.assertEqual(record.status, Attendance.Status.PRESENT)

        # Verify audit log was recorded
        from .models import AuditLog
        audit = AuditLog.objects.filter(
            action="ATTENDANCE_MODIFIED",
            entity_id=str(record.id),
        ).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.old_value, "ABSENT")
        self.assertEqual(audit.new_value, "PRESENT")
        self.assertEqual(audit.user, self.faculty1_user)

    def test_tc_att_03_modify_attendance_unauthorized_blocked(self):
        """TC-ATT-03: Non-assigned faculty or student cannot modify attendance."""
        self.client.login(username="faculty2", password="TestPassword123!")
        url = reverse("modify_attendance", args=[self.session1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        self.client.logout()
        self.client.login(username="student1", password="TestPassword123!")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_tc_view_01_student_view_own_attendance_only(self):
        """TC-VIEW-01: Student views only their own attendance data (SAM-F-017)."""
        self.client.login(username="student1", password="TestPassword123!")
        url = reverse("student_attendance")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "STU001")
        self.assertNotContains(response, "STU002")

        # Faculty should not have access to student portal endpoint
        self.client.logout()
        self.client.login(username="faculty1", password="TestPassword123!")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_tc_view_02_faculty_view_assigned_classes_only(self):
        """TC-VIEW-02: Faculty sees attendance records only for assigned classes (SAM-F-019)."""
        self.client.login(username="faculty1", password="TestPassword123!")
        url = reverse("faculty_dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CS201")
        self.assertNotContains(response, "EC201")

    def test_tc_hist_01_student_attendance_history(self):
        """TC-HIST-01: Past attendance records are maintained and viewable (SAM-F-024)."""
        Attendance.objects.create(
            session=self.session2,
            student=self.student1,
            status=Attendance.Status.LATE,
            marked_by=self.faculty1_user,
        )

        self.client.login(username="student1", password="TestPassword123!")
        response = self.client.get(reverse("student_attendance"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "20 Oct 2026")
        self.assertContains(response, "22 Oct 2026")
        self.assertContains(response, "Late")
        self.assertContains(response, "Present")

    def test_tc_calc_01_attendance_percentage_calculation(self):
        """TC-CALC-01: Attendance percentage calculation is accurate (SAM-F-018)."""
        from .services import calculate_percentage, student_subject_summary

        self.assertEqual(calculate_percentage(0, 0), 0.0)
        self.assertEqual(calculate_percentage(3, 4), 75.0)
        self.assertEqual(calculate_percentage(1, 3), 33.33)

        # Student 1: 1 present out of 1 session in CS201 = 100%
        summary1 = student_subject_summary(self.student1, self.subject1)
        self.assertEqual(summary1["total"], 1)
        self.assertEqual(summary1["percentage"], 100.0)
        self.assertFalse(summary1["is_low"])

        # Student 2: 0 present/late out of 1 session in CS201 = 0%
        summary2 = student_subject_summary(self.student2, self.subject1)
        self.assertEqual(summary2["total"], 1)
        self.assertEqual(summary2["percentage"], 0.0)
        self.assertTrue(summary2["is_low"])

    def test_tc_calc_02_low_attendance_identification(self):
        """TC-CALC-02: Students below configured threshold are flagged (SAM-F-020)."""
        from .services import low_attendance_students

        defaulters = low_attendance_students(self.subject1, threshold=75)
        self.assertEqual(len(defaulters), 1)
        self.assertEqual(defaulters[0]["student"], self.student2)

        # Defaulters view
        self.client.login(username="faculty1", password="TestPassword123!")
        url = reverse("defaulters_list", args=[self.subject1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "STU002")
        self.assertNotContains(response, "STU001")

    def test_tc_rep_01_attendance_report_criteria(self):
        """TC-REP-01: Attendance reports filtered by criteria (SAM-F-021)."""
        self.client.login(username="faculty1", password="TestPassword123!")
        url = reverse("attendance_reports")

        # Filter by subject
        response = self.client.get(url, {"subject": self.subject1.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "STU001")
        self.assertContains(response, "STU002")

        # Filter by student ID
        response = self.client.get(url, {"student": "STU001"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "STU001")
        self.assertNotContains(response, "STU002")

    def test_tc_rep_02_attendance_summaries_and_csv_export(self):
        """TC-REP-02: Attendance summary statistics and CSV export (SAM-F-022)."""
        self.client.login(username="faculty1", password="TestPassword123!")
        url = reverse("attendance_reports")

        # Check CSV export
        response = self.client.get(url, {"format": "csv"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode("utf-8")
        self.assertIn("Student ID,Student Name", content)
        self.assertIn("STU001", content)
        self.assertIn("STU002", content)

    def test_tc_not_01_low_attendance_notification(self):
        """TC-NOT-01: Student receives alert when attendance < threshold (SAM-F-023)."""
        # Student 2 is at 0% in CS201 (below 75%)
        self.client.login(username="student2", password="TestPassword123!")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Low Attendance Alert")

        response = self.client.get(reverse("student_attendance"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Low Attendance Notification")

        # Student 1 is at 100% (above 75%)
        self.client.logout()
        self.client.login(username="student1", password="TestPassword123!")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Low Attendance Alert")

    def test_tc_audit_01_and_sec_05_audit_logging(self):
        """TC-AUDIT-01 & TC-SEC-05: Actions are logged and inspectable by Admin (SAM-NF-006, SAM-SR-005)."""
        from .models import AuditLog

        initial_count = AuditLog.objects.count()
        self.client.login(username="faculty1", password="TestPassword123!")

        # Create new session triggers audit log
        self.client.post(
            reverse("create_attendance_session", args=[self.subject1.id]),
            {"session_date": "2026-10-25"},
        )
        self.assertGreater(AuditLog.objects.count(), initial_count)

        # Admin can view audit logs
        self.client.logout()
        self.client.login(username="admin_user", password="AdminPassword123!")
        response = self.client.get(reverse("audit_logs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SESSION_CREATED")

        # Student cannot view audit logs
        self.client.logout()
        self.client.login(username="student1", password="TestPassword123!")
        response = self.client.get(reverse("audit_logs"))
        self.assertEqual(response.status_code, 403)

    def test_tc_rel_01_health_check_endpoint(self):
        """TC-REL-01: Health check endpoint confirms system availability (SAM-NF-002)."""
        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("database"), "connected")

    def test_tc_perf_01_response_time(self):
        """TC-PERF-01: Key attendance endpoints respond well within 3 seconds (SAM-NF-001)."""
        import time

        self.client.login(username="faculty1", password="TestPassword123!")
        start = time.perf_counter()
        response = self.client.get(reverse("attendance_reports"))
        duration = time.perf_counter() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 3.0)
