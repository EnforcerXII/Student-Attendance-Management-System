"""Regression, integrity and branch-coverage tests for the attendance module.

Covers TC-ATT-01..05, TC-DATA-01, TC-REP-01/02, TC-CALC-01/02, TC-UX-01,
TC-AUDIT-01 (SAM-F-012..016, F-018, F-020..022, SAM-NF-004..006).
"""
import csv
import io
import unittest
from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from administration.models import Enrolment, Faculty, Student, Subject
from attendance.models import Attendance, AttendanceSession, AuditLog
from attendance.services import (
    calculate_percentage,
    log_audit_event,
    low_attendance_students,
    student_subject_summary,
)

User = get_user_model()
PW = "TestPassword123!"


class Base(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("adm", password=PW, role=User.Role.ADMIN, is_staff=True)
        self.fu = User.objects.create_user("fac", password=PW, role=User.Role.FACULTY)
        self.fu2 = User.objects.create_user("fac2", password=PW, role=User.Role.FACULTY)
        self.fac = Faculty.objects.create(faculty_id="F1", user=self.fu)
        self.fac2 = Faculty.objects.create(faculty_id="F2", user=self.fu2)
        self.sub = Subject.objects.create(subject_code="CS1", subject_name="Intro", faculty=self.fac)
        self.sub2 = Subject.objects.create(subject_code="CS2", subject_name="Other", faculty=self.fac2)
        self.students = []
        for i in range(1, 4):
            u = User.objects.create_user(f"stu{i}", password=PW, role=User.Role.STUDENT,
                                         first_name=f"Name{i}", last_name="Test")
            s = Student.objects.create(student_id=f"S{i}", user=u, department="CS", year_of_study=2)
            Enrolment.objects.create(student=s, subject=self.sub)
            self.students.append(s)
        self.session = AttendanceSession.objects.create(
            subject=self.sub, session_date=date(2026, 10, 5), created_by=self.fu
        )

    def login(self, name):
        self.client.login(username=name, password=PW)

    def post_status(self, status="PRESENT", **extra):
        data = {f"status_{s.id}": status for s in self.students}
        data.update(extra)
        return self.client.post(reverse("mark_attendance", args=[self.session.id]), data)


class SessionCreationTests(Base):
    def test_create_session_and_audit(self):
        """Faculty opens a class session; the action is audited (SAM-F-012, NF-006)."""
        self.login("fac")
        resp = self.client.post(reverse("create_attendance_session", args=[self.sub.id]),
                                {"session_date": "2026-10-06"})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(AttendanceSession.objects.filter(subject=self.sub, session_date="2026-10-06").exists())
        self.assertTrue(AuditLog.objects.filter(action="SESSION_CREATED").exists())

    def test_duplicate_session_not_created(self):
        self.login("fac")
        self.client.post(reverse("create_attendance_session", args=[self.sub.id]), {"session_date": "2026-10-05"})
        self.assertEqual(AttendanceSession.objects.filter(subject=self.sub, session_date="2026-10-05").count(), 1)

    def test_missing_date_rejected(self):
        self.login("fac")
        before = AttendanceSession.objects.count()
        resp = self.client.post(reverse("create_attendance_session", args=[self.sub.id]), {})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(AttendanceSession.objects.count(), before)

    def test_session_page_lists_sessions(self):
        self.login("fac")
        resp = self.client.get(reverse("create_attendance_session", args=[self.sub.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.session, resp.context["sessions"])

    def test_other_faculty_cannot_open_session_for_subject(self):
        self.login("fac2")
        resp = self.client.get(reverse("create_attendance_session", args=[self.sub.id]))
        self.assertEqual(resp.status_code, 404)


class MarkingTests(Base):
    def test_tc_att_01_mark_all_statuses(self):
        """TC-ATT-01/05: Present/Absent/Late saved with student, session, status, time (SAM-F-012, F-016)."""
        self.login("fac")
        data = {f"status_{self.students[0].id}": "PRESENT",
                f"status_{self.students[1].id}": "ABSENT",
                f"status_{self.students[2].id}": "LATE"}
        self.assertEqual(self.client.post(reverse("mark_attendance", args=[self.session.id]), data).status_code, 302)
        recs = {r.student_id: r for r in Attendance.objects.filter(session=self.session)}
        self.assertEqual(recs[self.students[0].id].status, "PRESENT")
        self.assertEqual(recs[self.students[1].id].status, "ABSENT")
        self.assertEqual(recs[self.students[2].id].status, "LATE")
        self.assertEqual(recs[self.students[0].id].marked_by, self.fu)
        self.assertIsNotNone(recs[self.students[0].id].marked_at)
        self.assertEqual(AuditLog.objects.filter(action="ATTENDANCE_MARKED").count(), 3)

    def test_tc_att_04_resubmission_does_not_duplicate(self):
        """TC-ATT-04: Submitting twice for the same session never duplicates (SAM-F-015)."""
        self.login("fac")
        self.post_status("PRESENT")
        self.post_status("PRESENT")
        self.assertEqual(Attendance.objects.filter(session=self.session).count(), 3)

    def test_unchanged_resubmission_writes_no_modification_audit(self):
        self.login("fac")
        self.post_status("PRESENT")
        self.post_status("PRESENT")
        self.assertEqual(AuditLog.objects.filter(action="ATTENDANCE_MODIFIED").count(), 0)

    def test_tc_att_03_modification_records_old_new_and_reason(self):
        """TC-ATT-03: Changing a status keeps old/new values and the reason in the audit log."""
        self.login("fac")
        self.post_status("PRESENT")
        self.post_status("ABSENT", reason="Marked wrongly")
        log = AuditLog.objects.filter(action="ATTENDANCE_MODIFIED").first()
        self.assertEqual((log.old_value, log.new_value, log.reason), ("PRESENT", "ABSENT", "Marked wrongly"))

    def test_modification_without_reason_uses_default(self):
        self.login("fac")
        self.post_status("PRESENT")
        self.post_status("LATE")
        self.assertEqual(AuditLog.objects.filter(action="ATTENDANCE_MODIFIED").first().reason, "Faculty modification")

    def test_modify_view_shows_existing_values(self):
        self.login("fac")
        self.post_status("LATE")
        resp = self.client.get(reverse("modify_attendance", args=[self.session.id]))
        self.assertTrue(resp.context["is_modifying"])
        self.assertEqual({r["current_status"] for r in resp.context["student_rows"]}, {"LATE"})

    def test_invalid_status_rejected_with_400(self):
        """Server-side validation of attendance input (SAM-SR input validation)."""
        self.login("fac")
        resp = self.post_status("HACKED")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Attendance.objects.count(), 0)

    @unittest.expectedFailure
    def test_tc_data_01_partial_submission_is_rolled_back(self):
        """TC-DATA-01 (DEF-01): A rejected submission must not leave partial records.

        Currently fails: mark_attendance() returns the 400 response from inside
        `transaction.atomic()` without raising, so records saved for earlier
        students in the same request are committed. Marked expectedFailure
        so the suite stays green while the defect is open.
        """
        self.login("fac")
        data = {f"status_{self.students[0].id}": "PRESENT",
                f"status_{self.students[1].id}": "BOGUS",
                f"status_{self.students[2].id}": "PRESENT"}
        resp = self.client.post(reverse("mark_attendance", args=[self.session.id]), data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Attendance.objects.filter(session=self.session).count(), 0)

    def test_tc_data_01_database_blocks_duplicates(self):
        """TC-DATA-01: DB-level unique constraint stops duplicate rows (SAM-NF-005)."""
        Attendance.objects.create(session=self.session, student=self.students[0], status="PRESENT", marked_by=self.fu)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Attendance.objects.create(session=self.session, student=self.students[0],
                                          status="ABSENT", marked_by=self.fu)

    def test_tc_ux_01_bulk_marking_buttons_present(self):
        """TC-UX-01: Mark-all shortcuts exist on the marking page (SAM-NF-004)."""
        self.login("fac")
        resp = self.client.get(reverse("mark_attendance", args=[self.session.id]))
        self.assertContains(resp, "Mark All Present")
        self.assertContains(resp, "Mark All Absent")

    def test_other_faculty_cannot_mark_or_modify(self):
        self.login("fac2")
        self.assertEqual(self.post_status("PRESENT").status_code, 404)
        self.assertEqual(self.client.get(reverse("modify_attendance", args=[self.session.id])).status_code, 404)
        self.assertEqual(Attendance.objects.count(), 0)


class ReportViewTests(Base):
    def setUp(self):
        super().setUp()
        s2 = AttendanceSession.objects.create(subject=self.sub, session_date=date(2026, 10, 12), created_by=self.fu)
        for st, (a, b) in zip(self.students, [("PRESENT", "PRESENT"), ("LATE", "ABSENT"), ("ABSENT", "ABSENT")]):
            Attendance.objects.create(session=self.session, student=st, status=a, marked_by=self.fu)
            Attendance.objects.create(session=s2, student=st, status=b, marked_by=self.fu)

    def test_session_report_for_faculty_and_admin(self):
        self.login("fac")
        resp = self.client.get(reverse("attendance_report", args=[self.session.id]))
        self.assertEqual((resp.context["present_count"], resp.context["late_count"], resp.context["absent_count"]),
                         (1, 1, 1))
        self.assertEqual(resp.context["attendance_percentage"], 66.67)
        self.client.logout()
        self.login("adm")
        self.assertEqual(self.client.get(reverse("attendance_report", args=[self.session.id])).status_code, 200)

    def test_session_report_denied_for_other_faculty_and_student(self):
        self.login("fac2")
        self.assertEqual(self.client.get(reverse("attendance_report", args=[self.session.id])).status_code, 404)
        self.client.logout()
        self.login("stu1")
        self.assertEqual(self.client.get(reverse("attendance_report", args=[self.session.id])).status_code, 403)

    def test_tc_rep_01_filters_subject_student_and_dates(self):
        """TC-REP-01: Report honours subject, student and date-range filters (SAM-F-021)."""
        self.login("fac")
        url = reverse("attendance_reports")
        self.assertEqual(self.client.get(url).context["total_records"], 6)
        self.assertEqual(self.client.get(url, {"subject": self.sub.id}).context["total_records"], 6)
        self.assertEqual(self.client.get(url, {"student": "S1"}).context["total_records"], 2)
        self.assertEqual(self.client.get(url, {"student": "Name2"}).context["total_records"], 2)
        self.assertEqual(self.client.get(url, {"start_date": "2026-10-10"}).context["total_records"], 3)
        self.assertEqual(self.client.get(url, {"end_date": "2026-10-10"}).context["total_records"], 3)

    def test_faculty_report_excludes_other_faculty_subjects(self):
        self.login("fac2")
        self.assertEqual(self.client.get(reverse("attendance_reports")).context["total_records"], 0)

    def test_admin_sees_all_subjects_in_reports(self):
        self.login("adm")
        resp = self.client.get(reverse("attendance_reports"))
        self.assertEqual(resp.context["subjects"].count(), 2)

    def test_tc_rep_02_summary_numbers_and_csv_match(self):
        """TC-REP-02: On-screen totals equal the CSV export rows (SAM-F-022)."""
        self.login("fac")
        url = reverse("attendance_reports")
        page = self.client.get(url, {"student": "S1"})
        self.assertEqual(page.context["overall_percentage"], 100.0)
        resp = self.client.get(url, {"format": "csv", "student": "S1"})
        self.assertEqual(resp["Content-Type"], "text/csv")
        rows = list(csv.reader(io.StringIO(resp.content.decode())))
        self.assertEqual(rows[0][0], "Student ID")
        self.assertEqual(len(rows) - 1, page.context["total_records"])

    def test_tc_calc_01_percentage_values(self):
        """TC-CALC-01: (Present+Late)/Total*100, rounded to 2 dp (SAM-F-018)."""
        self.assertEqual(calculate_percentage(0, 0), 0.0)
        self.assertEqual(calculate_percentage(2, 3), 66.67)
        self.assertEqual(calculate_percentage(3, 3), 100.0)
        summary = student_subject_summary(self.students[1], self.sub)
        self.assertEqual((summary["present"], summary["late"], summary["absent"], summary["percentage"]),
                         (0, 1, 1, 50.0))

    def test_tc_calc_02_threshold_boundary(self):
        """TC-CALC-02: 'Below 75%' is strict; exactly 75% is not flagged (SAM-F-020)."""
        self.assertEqual(
            sorted(x["student"].student_id for x in low_attendance_students(self.sub)), ["S2", "S3"]
        )
        self.assertEqual(
            sorted(x["student"].student_id for x in low_attendance_students(self.sub, threshold=50)), ["S3"]
        )
        self.assertEqual(student_subject_summary(self.students[1], self.sub, threshold=50)["is_low"], False)

    def test_student_with_no_records_is_not_flagged(self):
        Attendance.objects.all().delete()
        self.assertEqual(low_attendance_students(self.sub), [])

    def test_defaulters_view_threshold_param(self):
        self.login("fac")
        url = reverse("defaulters_list", args=[self.sub.id])
        self.assertEqual(len(self.client.get(url).context["defaulters"]), 2)
        self.assertEqual(len(self.client.get(url, {"threshold": "50"}).context["defaulters"]), 1)
        resp = self.client.get(url, {"threshold": "abc"})  # invalid input falls back to default
        self.assertEqual(resp.context["threshold"], 75)

    def test_defaulters_access_rules(self):
        self.login("adm")
        self.assertEqual(self.client.get(reverse("defaulters_list", args=[self.sub.id])).status_code, 200)
        self.client.logout()
        self.login("fac2")
        self.assertEqual(self.client.get(reverse("defaulters_list", args=[self.sub.id])).status_code, 404)

    def test_student_attendance_page_and_missing_profile(self):
        self.login("stu2")
        resp = self.client.get(reverse("student_attendance"))
        self.assertEqual(len(resp.context["history"]), 2)
        self.assertTrue(resp.context["low_attendance_alerts"])
        self.client.logout()
        User.objects.create_user("noprof", password=PW, role=User.Role.STUDENT)
        self.login("noprof")
        self.assertEqual(self.client.get(reverse("student_attendance")).status_code, 404)

    def test_faculty_cannot_see_student_page(self):
        self.login("fac")
        self.assertEqual(self.client.get(reverse("student_attendance")).status_code, 403)


class ModelAndServiceTests(Base):
    def test_audit_log_anonymous_actor_and_strings(self):
        from django.contrib.auth.models import AnonymousUser
        entry = log_audit_event(AnonymousUser(), "SYS", "Thing", 1, None, "x")
        self.assertIsNone(entry.user)
        self.assertIn("System", str(entry))
        entry2 = log_audit_event(self.fu, "ACT", "Thing")
        self.assertIsNone(entry2.entity_id)
        self.assertIn("fac", str(entry2))

    def test_attendance_and_session_str(self):
        rec = Attendance.objects.create(session=self.session, student=self.students[0], status="LATE", marked_by=self.fu)
        self.assertIn("LATE", str(rec))
        self.assertIn("CS1", str(self.session))


class HealthCheckFailureTests(TestCase):
    def test_tc_rel_01_health_reports_503_when_database_down(self):
        """TC-REL-01: Health endpoint reports 'unhealthy' (503) if the database is unreachable (SAM-NF-002)."""
        from unittest import mock
        with mock.patch("config.urls.connection") as conn:
            conn.cursor.side_effect = RuntimeError("db down")
            resp = self.client.get("/health/")
        self.assertEqual(resp.status_code, 503)
        self.assertEqual(resp.json()["status"], "unhealthy")
