"""Admin management tests: students, faculty, subjects, assignment, enrolment, audit view.

Covers TC-STU-01..03, TC-FAC-01..02, TC-SUB-01, TC-ENR-01 (SAM-F-005..011).
"""
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from administration.models import Enrolment, Faculty, Student, Subject
from attendance.services import log_audit_event

User = get_user_model()
PW = "TestPassword123!"


class AdminManagementTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("root", password=PW, role=User.Role.ADMIN)
        self.client.login(username="root", password=PW)
        self.fac_user = User.objects.create_user("prof", password=PW, role=User.Role.FACULTY)
        self.faculty = Faculty.objects.create(faculty_id="F1", user=self.fac_user, department="CS")

    def _student(self, n=1, **kw):
        u = User.objects.create_user(f"s{n}", password=PW, role=User.Role.STUDENT,
                                     first_name="Ann", last_name=f"Lee{n}")
        return Student.objects.create(student_id=f"S{n}", user=u, department="CS", year_of_study=1, **kw)

    def test_tc_stu_01_admin_adds_student(self):
        """TC-STU-01: Admin adds a student through the admin portal (SAM-F-005)."""
        u = User.objects.create_user("newstu", password=PW, role=User.Role.STUDENT)
        resp = self.client.post(
            reverse("admin:administration_student_add"),
            {"student_id": "S900", "user": u.id, "department": "ECE", "year_of_study": 3},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Student.objects.filter(student_id="S900", department="ECE").exists())

    def test_tc_stu_01_duplicate_student_id_rejected(self):
        self._student(1)
        u = User.objects.create_user("dup", password=PW, role=User.Role.STUDENT)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Student.objects.create(student_id="S1", user=u)

    def test_tc_stu_02_admin_updates_student(self):
        """TC-STU-02: Updated student information is saved (SAM-F-006)."""
        s = self._student(1)
        resp = self.client.post(
            reverse("admin:administration_student_change", args=[s.id]),
            {"student_id": "S1", "user": s.user_id, "department": "Mechanical", "year_of_study": 4},
        )
        self.assertEqual(resp.status_code, 302)
        s.refresh_from_db()
        self.assertEqual((s.department, s.year_of_study), ("Mechanical", 4))

    def test_tc_stu_03_admin_lists_students(self):
        """TC-STU-03: Admin can view the student list (SAM-F-007)."""
        self._student(1)
        self._student(2)
        resp = self.client.get(reverse("admin:administration_student_changelist"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "S1")
        self.assertContains(resp, "S2")

    def test_tc_fac_01_admin_creates_faculty_who_can_login(self):
        """TC-FAC-01: A created faculty account can log in (SAM-F-008)."""
        self.client.logout()
        self.assertTrue(self.client.login(username="prof", password=PW))
        self.assertEqual(self.client.get(reverse("faculty_dashboard")).status_code, 200)

    def test_tc_sub_01_subject_created_and_code_unique(self):
        """TC-SUB-01: Subject stored; subject codes are unique (SAM-F-009)."""
        Subject.objects.create(subject_code="CS101", subject_name="A", faculty=self.faculty)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Subject.objects.create(subject_code="CS101", subject_name="B", faculty=self.faculty)

    def test_tc_fac_02_assigned_faculty_sees_subject(self):
        """TC-FAC-02: Assigned faculty sees the subject on their dashboard (SAM-F-010)."""
        Subject.objects.create(subject_code="CS101", subject_name="A", faculty=self.faculty)
        self.client.logout()
        self.client.login(username="prof", password=PW)
        resp = self.client.get(reverse("faculty_dashboard"))
        self.assertContains(resp, "CS101")

    def test_tc_enr_01_enrolled_student_appears_in_marking_list(self):
        """TC-ENR-01: Enrolled students appear in the faculty attendance list (SAM-F-011)."""
        sub = Subject.objects.create(subject_code="CS101", subject_name="A", faculty=self.faculty)
        s1, s2 = self._student(1), self._student(2)
        Enrolment.objects.create(student=s1, subject=sub)
        from attendance.models import AttendanceSession
        sess = AttendanceSession.objects.create(subject=sub, session_date="2026-10-01", created_by=self.fac_user)
        self.client.logout()
        self.client.login(username="prof", password=PW)
        resp = self.client.get(reverse("mark_attendance", args=[sess.id]))
        shown = [r["student"].student_id for r in resp.context["student_rows"]]
        self.assertEqual(shown, ["S1"])
        self.assertNotIn(s2.student_id, shown)

    def test_model_string_representations(self):
        sub = Subject.objects.create(subject_code="CS101", subject_name="A", faculty=self.faculty)
        s = self._student(1)
        en = Enrolment.objects.create(student=s, subject=sub)
        self.assertIn("S1", str(s))
        self.assertIn("F1", str(self.faculty))
        self.assertEqual(str(sub), "CS101 - A")
        self.assertIn("CS101", str(en))

    def test_audit_log_view_lists_events_for_admin(self):
        log_audit_event(self.admin, "TEST_ACTION", "Thing", 7, "a", "b", "because")
        resp = self.client.get(reverse("audit_logs"))
        self.assertContains(resp, "TEST_ACTION")
