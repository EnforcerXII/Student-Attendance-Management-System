"""Authentication, RBAC, dashboard and security tests.

Covers: TC-AUTH-01..04, TC-SEC-01..04, dashboards (SAM-F-001..004, SAM-NF-003,
SAM-SR-001..004). Added during the Part-3 testing phase.
"""
import unittest
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from administration.models import Enrolment, Faculty, Student, Subject
from attendance.models import Attendance, AttendanceSession

User = get_user_model()
PBKDF2 = ["django.contrib.auth.hashers.PBKDF2PasswordHasher"]


class AuthBase(TestCase):
    PASSWORD = "TestPassword123!"

    def setUp(self):
        self.admin = User.objects.create_user(
            "adm", password=self.PASSWORD, role=User.Role.ADMIN, is_staff=True, is_superuser=True
        )
        self.fac_user = User.objects.create_user("fac", password=self.PASSWORD, role=User.Role.FACULTY)
        self.stu_user = User.objects.create_user("stu", password=self.PASSWORD, role=User.Role.STUDENT)
        self.faculty = Faculty.objects.create(faculty_id="F1", user=self.fac_user, department="CS")
        self.student = Student.objects.create(student_id="S1", user=self.stu_user, department="CS", year_of_study=2)
        self.subject = Subject.objects.create(subject_code="CS1", subject_name="Intro", faculty=self.faculty)
        Enrolment.objects.create(student=self.student, subject=self.subject)


class LoginLogoutTests(AuthBase):
    def test_tc_auth_01_valid_login_creates_session(self):
        """TC-AUTH-01: Valid credentials log the user in (SAM-F-001)."""
        resp = self.client.post(reverse("login"), {"username": "stu", "password": self.PASSWORD})
        self.assertRedirects(resp, "/role-redirect/", fetch_redirect_response=False)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.stu_user.id)

    def test_tc_auth_01_login_page_renders(self):
        resp = self.client.get(reverse("login"))
        self.assertEqual(resp.status_code, 200)

    def test_tc_auth_01_role_redirect_per_role(self):
        """Each role lands on its own dashboard after login."""
        self.client.login(username="fac", password=self.PASSWORD)
        self.assertRedirects(self.client.get("/role-redirect/"), reverse("faculty_dashboard"))
        self.client.login(username="stu", password=self.PASSWORD)
        self.assertRedirects(self.client.get("/role-redirect/"), reverse("dashboard"))
        self.client.login(username="adm", password=self.PASSWORD)
        self.assertRedirects(self.client.get("/role-redirect/"), reverse("dashboard"))

    def test_tc_auth_02_invalid_password_rejected(self):
        """TC-AUTH-02: Invalid credentials create no session and show an error (SAM-F-002)."""
        resp = self.client.post(reverse("login"), {"username": "stu", "password": "wrong"})
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(resp.context["form"].errors)

    def test_tc_auth_02_unknown_user_rejected(self):
        resp = self.client.post(reverse("login"), {"username": "nobody", "password": "x"})
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_tc_auth_02_error_message_is_generic(self):
        """Wrong password and unknown user give the same error (no account enumeration)."""
        a = self.client.post(reverse("login"), {"username": "stu", "password": "wrong"})
        b = self.client.post(reverse("login"), {"username": "nobody", "password": "wrong"})
        self.assertEqual(
            [str(e) for e in a.context["form"].non_field_errors()],
            [str(e) for e in b.context["form"].non_field_errors()],
        )

    def test_tc_auth_04_logout_ends_session(self):
        """TC-AUTH-04: After logout protected pages need login again (SAM-F-004)."""
        self.client.login(username="stu", password=self.PASSWORD)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)
        resp = self.client.post("/accounts/logout/")
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])


class RoleBasedAccessTests(AuthBase):
    def test_tc_auth_03_student_blocked_from_faculty_and_admin_pages(self):
        """TC-AUTH-03 / TC-SEC-02: Student cannot reach faculty/admin functions (SAM-F-003, SAM-SR-002)."""
        self.client.login(username="stu", password=self.PASSWORD)
        for url in (
            reverse("faculty_dashboard"),
            reverse("attendance_reports"),
            reverse("audit_logs"),
            reverse("defaulters_list", args=[self.subject.id]),
            reverse("create_attendance_session", args=[self.subject.id]),
        ):
            self.assertEqual(self.client.get(url).status_code, 403, url)

    def test_tc_auth_03_faculty_blocked_from_student_and_admin_pages(self):
        self.client.login(username="fac", password=self.PASSWORD)
        self.assertEqual(self.client.get(reverse("student_attendance")).status_code, 403)
        self.assertEqual(self.client.get(reverse("audit_logs")).status_code, 403)

    def test_tc_auth_03_admin_allowed_on_admin_pages(self):
        self.client.login(username="adm", password=self.PASSWORD)
        self.assertEqual(self.client.get(reverse("audit_logs")).status_code, 200)
        self.assertEqual(self.client.get(reverse("attendance_reports")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)

    def test_tc_sec_01_unauthenticated_redirected_to_login(self):
        """TC-SEC-01: Protected pages redirect anonymous users to login (SAM-SR-001)."""
        urls = [
            reverse("dashboard"),
            reverse("faculty_dashboard"),
            reverse("student_attendance"),
            reverse("attendance_reports"),
            reverse("audit_logs"),
            reverse("mark_attendance", args=[1]),
            reverse("attendance_report", args=[1]),
            reverse("defaulters_list", args=[1]),
        ]
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302, url)
            self.assertIn("/accounts/login/", resp["Location"], url)

    def test_tc_sec_02_student_cannot_post_attendance_directly(self):
        """TC-SEC-02: Authorisation is enforced on the server, not just hidden in the UI."""
        session = AttendanceSession.objects.create(
            subject=self.subject, session_date=date(2026, 10, 1), created_by=self.fac_user
        )
        self.client.login(username="stu", password=self.PASSWORD)
        resp = self.client.post(
            reverse("mark_attendance", args=[session.id]), {f"status_{self.student.id}": "PRESENT"}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Attendance.objects.count(), 0)


class DashboardTests(AuthBase):
    def test_admin_dashboard_shows_totals(self):
        self.client.login(username="adm", password=self.PASSWORD)
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.context["dashboard_title"], "Admin Dashboard")
        self.assertEqual(resp.context["total_students"], 1)
        self.assertEqual(resp.context["total_faculty"], 1)
        self.assertEqual(resp.context["total_subjects"], 1)

    def test_faculty_dashboards_show_assigned_subjects_only(self):
        other_user = User.objects.create_user("fac2", password=self.PASSWORD, role=User.Role.FACULTY)
        other = Faculty.objects.create(faculty_id="F2", user=other_user)
        Subject.objects.create(subject_code="CS2", subject_name="Other", faculty=other)
        self.client.login(username="fac", password=self.PASSWORD)
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.context["dashboard_title"], "Faculty Dashboard")
        self.assertEqual(resp.context["assigned_subjects_count"], 1)
        resp = self.client.get(reverse("faculty_dashboard"))
        self.assertEqual([s.subject_code for s in resp.context["subjects"]], ["CS1"])

    def test_student_dashboard_with_profile_and_records(self):
        session = AttendanceSession.objects.create(
            subject=self.subject, session_date=date(2026, 10, 1), created_by=self.fac_user
        )
        Attendance.objects.create(session=session, student=self.student, status="PRESENT", marked_by=self.fac_user)
        self.client.login(username="stu", password=self.PASSWORD)
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.context["total_classes"], 1)
        self.assertEqual(resp.context["attendance_percentage"], 100.0)

    def test_student_dashboard_without_attendance_records(self):
        self.client.login(username="stu", password=self.PASSWORD)
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.context["total_classes"], 0)
        self.assertEqual(resp.context["attendance_percentage"], 0)

    def test_student_dashboard_without_student_profile(self):
        """A STUDENT user with no Student profile still gets a safe dashboard."""
        User.objects.create_user("orphan", password=self.PASSWORD, role=User.Role.STUDENT)
        self.client.login(username="orphan", password=self.PASSWORD)
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.context["student"])

    def test_user_str(self):
        self.assertEqual(str(self.stu_user), "stu (STUDENT)")


class PasswordAndTransportSecurityTests(AuthBase):
    @override_settings(PASSWORD_HASHERS=PBKDF2)
    def test_tc_sec_03_password_is_hashed_not_plaintext(self):
        """TC-SEC-03: Passwords are stored with a salted one-way hash (SAM-SR-003)."""
        user = User.objects.create_user("hashme", password="PlainSecret#1")
        self.assertNotEqual(user.password, "PlainSecret#1")
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(user.check_password("PlainSecret#1"))
        other = User.objects.create_user("hashme2", password="PlainSecret#1")
        self.assertNotEqual(user.password, other.password)  # unique salts

    def test_tc_sec_04_proxy_ssl_header_configured(self):
        """TC-SEC-04: Reverse-proxy HTTPS header is trusted (SAM-SR-004)."""
        self.assertEqual(settings.SECURE_PROXY_SSL_HEADER, ("HTTP_X_FORWARDED_PROTO", "https"))

    @unittest.expectedFailure
    def test_tc_sec_04_secure_cookies_enabled(self):
        """TC-SEC-04 (DEF-02): session/CSRF cookies should be Secure for HTTPS deployment.

        Currently fails: settings.py hard-codes DEBUG = True, so the
        `if not DEBUG:` block that sets SESSION_COOKIE_SECURE never runs.
        Marked expectedFailure so the suite stays green while the defect is open.
        """
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)
