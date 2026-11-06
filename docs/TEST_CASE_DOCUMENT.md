# Test Case Document

Student Attendance Management System (SAMS)

| | |
|---|---|
| Project | Student Attendance Management System (SAMS) |
| Version | 2.0 |
| Authors | Atul Kandiyil (PES2UG24CS920), Riona Jeena Dsouza (PES2UG24CS654), Amit (PES2UG24CS624) - Team 1 |
| Date | 06-11-2026 |
| Build tested | main branch, commit 33cdb28, plus the new test files |
| Environment | Python 3.12.3, Django 5.2.18, SQLite, Linux |

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 2.0 | 06-11-2026 | Team 1 | Updated from the test cases in the Test Plan v1.0 after Sprint 1 and Sprint 2. |

## Approvals

| Role | Name | Signature / Date |
|---|---|---|
| Team Lead | Atul Kandiyil | |
| Dev Lead | Riona Jeena Dsouza | |
| Test Engineer | Amit | |

## 1. Introduction

This document is the updated set of test cases for SAMS. The first set was written for the Software Test Plan (16-09-2026) and the acceptance tests in the SRS. Since then we built Sprint 1 and Sprint 2, and a few things came out different from what we planned, so we went through every test case and changed it to match the system that exists now. The test case IDs are the same as before so the traceability matrix in the SRS still lines up.

For each case the table in section 3 shows the steps and expected result, how it is tested (automated tests in the code, and a scenario on the running system), the result from this test round, and what changed from the first version.

## 2. What changed since version 1.0

- Attendance can now be Present, Absent or Late. The percentage is (Present + Late) / Total.
- The low-attendance limit is 75%, and a student is flagged only when strictly below it. It can be changed with a threshold value in the defaulters page URL.
- Students, faculty, subjects and enrolments are managed in the Django admin portal. We did not build separate pages for them.
- Changing a saved attendance record now writes an audit log entry with the old value, new value and reason. This is a new test case, TC-AUDIT-01.
- Sprint 2 added CSV export, the health check, the report filters and dashboards for each role, so there are new checks for them.
- Performance is tested with our own load script and a 100-thread run on the running server, instead of JMeter.
- The suite went from 20 automated tests to 83.
- Things in the SAD that are not in the SRS (QR and biometric capture, lockout after 5 failed logins, the 48-hour correction window) are not built and not tested. See OBS-02 in the System Validation Report.

## 3. Test cases

There are 35 test cases. 32 passed. The other 3 are partial, either because of an open defect or because a manual check has not been done yet.

| TC ID | Requirement | Title | Steps and expected result | Tested by | Result | Change since v1.0 |
|---|---|---|---|---|---|---|
| TC-AUTH-01 | SAM-F-001 | Valid login | Enter valid username and password on /accounts/login/. A session is created and the user lands on the dashboard for their role. | 3 unit, SV-04 | Pass | Changed: login now redirects through /role-redirect/ (faculty go to the faculty dashboard). |
| TC-AUTH-02 | SAM-F-002 | Invalid login rejected | Wrong password or unknown user. No session, an error is shown, and the message is the same in both cases. | 3 unit, SV-03 | Pass | Added the same-message check. |
| TC-AUTH-03 | SAM-F-003 | Role-based access | Open faculty/admin pages as a student, student pages as faculty, admin pages as admin. 403 outside the role, 200 inside it. | 3 unit, SV-07 | Pass | Now covers the Sprint 2 pages (reports, audit log, defaulters). |
| TC-AUTH-04 | SAM-F-004 | Logout | Log in, log out, open the dashboard. Redirected to login. | 1 unit, SV-20 | Pass | Changed: logout is a POST request in Django 5. |
| TC-STU-01 | SAM-F-005 | Add student | Admin adds a student in the admin portal. Record is saved, duplicate student ID is rejected. | 3 unit, SV-19 | Pass | Changed: done through the Django admin portal. |
| TC-STU-02 | SAM-F-006 | Update student | Admin edits department and year. The change is saved. | 1 unit, SV-19 | Pass | Changed: done through the Django admin portal. |
| TC-STU-03 | SAM-F-007 | View / search students | Admin opens the student list. Faculty and admin filter students by ID or name on the reports page. | 2 unit, SV-19, SV-15 | Pass | Changed: search is the student filter on the reports page (see OBS-04). |
| TC-FAC-01 | SAM-F-008 | Create faculty account | Admin creates a faculty user and profile. That faculty member can log in. | 1 unit, SV-19 | Pass | Changed: done through the Django admin portal. |
| TC-SUB-01 | SAM-F-009 | Manage subjects | Create a subject. It is saved and the subject code must be unique. | 1 unit, SV-19 | Pass | No change. |
| TC-FAC-02 | SAM-F-010 | Assign faculty to subject | Assign faculty to a subject. It shows on that faculty member's dashboard and nobody else's. | 2 unit, SV-09 | Pass | Added the check that other faculty do not see it. |
| TC-ENR-01 | SAM-F-011 | Student enrolment | Enrol students in a subject. Only enrolled students appear in the marking list. A duplicate enrolment is rejected. | 2 unit, SV-11 | Pass | No change. |
| TC-ATT-01 | SAM-F-012 | Mark attendance | Faculty opens a session and marks Present, Absent or Late for every enrolled student. Records are saved and an audit entry is written. | 8 unit, SV-10, SV-11 | Pass | Changed: Late added as a status; session creation and the mark-all buttons added. |
| TC-ATT-02 | SAM-F-013 | Block unauthorised marking | A student, or faculty who do not teach the subject, try to mark attendance (page and direct POST). 403 or 404 and nothing is saved. | 3 unit, SV-08 | Pass | Added the direct POST and other-faculty cases. |
| TC-ATT-03 | SAM-F-014 | Modify attendance | Assigned faculty change a saved status and give a reason. The record is updated and the audit log keeps the old value, new value and reason. | 6 unit, SV-13 | Pass | Changed: reason is recorded. There is no time limit on modifying (OBS-02). |
| TC-ATT-04 | SAM-F-015 | Prevent duplicates | Submit the same session twice, or insert a second record for the same student and session. Only one record exists. | 3 unit, SV-10, SV-12 | Pass | Added the re-submission case from the UI. |
| TC-ATT-05 | SAM-F-016 | Store attendance details | A saved record has the student, session (subject and date), status, who marked it and when. | 2 unit, SV-11 | Pass | No change. |
| TC-VIEW-01 | SAM-F-017 | Student views own attendance | Student opens /attendance/my/ and sees only their own records. | 2 unit, SV-05 | Pass | Added: a student user with no student profile gets a 404. |
| TC-VIEW-02 | SAM-F-019 | Faculty views assigned classes | The faculty dashboard lists only the subjects assigned to that faculty member. | 1 unit, SV-09 | Pass | No change. |
| TC-CALC-01 | SAM-F-018 | Attendance percentage | Percentage = (Present + Late) / Total x 100, 2 decimal places, 0 if there are no classes. | 2 unit, SV-05 | Pass | Changed: Late counts as attended. Boundary values added. |
| TC-CALC-02 | SAM-F-020 | Identify low attendance | Students strictly below 75% (or the ?threshold= value) are listed. Students with no records are not flagged. | 4 unit, SV-14 | Pass | Changed: threshold is 75% and can be changed in the URL. A bad value falls back to 75. |
| TC-HIST-01 | SAM-F-024 | Attendance history | Student sees earlier records, newest first. | 1 unit, SV-05 | Pass | No change. |
| TC-REP-01 | SAM-F-021 | Generate reports | Filter by subject, student and date range. Only matching records show. Faculty see their own subjects, admin sees all. | 6 unit, SV-15 | Pass | Added date range, student filter and role scoping. |
| TC-REP-02 | SAM-F-022 | Summaries and CSV export | The totals on screen match the rows in the CSV export. | 2 unit, SV-15 | Pass | Changed: CSV export was added in Sprint 2. |
| TC-NOT-01 | SAM-F-023 | Low-attendance notification | A student below 75% sees a warning banner. A student above 75% does not. | 1 unit, SV-05, SV-06 | Pass | Changed: it is an on-screen banner, there is no email or SMS. |
| TC-PERF-01 | SAM-NF-001 | Response time (p95 under 3 s) | Key pages answer within 3 seconds and the load script gives p95 of 3 s or less. | 1 unit, SV-24 | Pass | Changed: our own load script is used instead of JMeter (Deviation 2). |
| TC-REL-01 | SAM-NF-002 | Availability / health check | /health/ gives 200 when the database is up and 503 when it is down. | 2 unit, SV-01 | Pass | New: health endpoint added in Sprint 2. |
| TC-SEC-01 | SAM-SR-001, SAM-NF-003 | Login required | Anonymous requests to protected pages are redirected to the login page. | 1 unit, SV-02 | Pass | Now covers all Sprint 2 URLs. |
| TC-SEC-02 | SAM-SR-002 | Roles enforced on the server | Requests from the wrong role (GET and POST) are refused. | 2 unit, SV-07, SV-08 | Pass | Extended. |
| TC-SEC-03 | SAM-SR-003 | Password hashing | Stored passwords are salted PBKDF2 hashes and never plain text. Two users with the same password get different hashes. | 1 unit, SV-21 | Pass | Changed: the test runner uses MD5 for speed (Deviation 3), so this is checked with PBKDF2 and on the live database. |
| TC-SEC-04 | SAM-SR-004 | HTTPS | The proxy SSL header is set and the session and CSRF cookies are marked Secure. | 2 unit, SV-22 | Partial (DEF-02) | Changed: now checks the cookie flags, which fails (DEF-02). Real TLS on a server was not tested (OBS-05). |
| TC-AUDIT-01 | SAM-NF-006 | Audit logging | Creating and modifying records writes an audit entry (user, action, entity, old and new value, reason, time). Only admin can read it. | 4 unit, SV-13, SV-18 | Pass | New: audit log added in Sprint 2. |
| TC-SEC-05 | SAM-SR-005 | Security activity logging | Important actions record the user and a timestamp. | 3 unit, SV-18 | Pass | Same checks as TC-AUDIT-01. |
| TC-UX-01 | SAM-NF-004 | Usability of marking | The mark-all buttons are on the marking page. A faculty member can mark a class without help. | 1 unit | Partial (manual trial pending) | Changed: mark-all buttons (Deviation 4). The manual user trial has not been done (OBS-05). |
| TC-DATA-01 | SAM-NF-005 | Data integrity | The database refuses duplicates, and a rejected submission leaves no partial data. | 2 unit, SV-23 | Partial (DEF-01) | Added the atomicity check, which fails (DEF-01). |
| TC-SCALE-01 | SAM-NF-007 | 100 concurrent users | 100 users at the same time with no errors. | SV-24 | Pass | Checked with performance_test.py and a 100-thread run on the live server. |

"Tested by" shows how many automated tests are linked to the case (listed in the Unit Test Report) and which system scenarios (SV-nn) in the System Validation Report cover it.

## 4. Traceability

| Requirement | Test case(s) | Status |
|---|---|---|
| SAM-F-001 | TC-AUTH-01 | Pass |
| SAM-F-002 | TC-AUTH-02 | Pass |
| SAM-F-003 | TC-AUTH-03 | Pass |
| SAM-F-004 | TC-AUTH-04 | Pass |
| SAM-F-005 | TC-STU-01 | Pass |
| SAM-F-006 | TC-STU-02 | Pass |
| SAM-F-007 | TC-STU-03 | Pass |
| SAM-F-008 | TC-FAC-01 | Pass |
| SAM-F-009 | TC-SUB-01 | Pass |
| SAM-F-010 | TC-FAC-02 | Pass |
| SAM-F-011 | TC-ENR-01 | Pass |
| SAM-F-012 | TC-ATT-01 | Pass |
| SAM-F-013 | TC-ATT-02 | Pass |
| SAM-F-014 | TC-ATT-03 | Pass |
| SAM-F-015 | TC-ATT-04 | Pass |
| SAM-F-016 | TC-ATT-05 | Pass |
| SAM-F-017 | TC-VIEW-01 | Pass |
| SAM-F-018 | TC-CALC-01 | Pass |
| SAM-F-019 | TC-VIEW-02 | Pass |
| SAM-F-020 | TC-CALC-02 | Pass |
| SAM-F-021 | TC-REP-01 | Pass |
| SAM-F-022 | TC-REP-02 | Pass |
| SAM-F-023 | TC-NOT-01 | Pass |
| SAM-F-024 | TC-HIST-01 | Pass |
| SAM-NF-001 | TC-PERF-01 | Pass |
| SAM-NF-002 | TC-REL-01 | Pass |
| SAM-NF-003 | TC-SEC-01 | Pass |
| SAM-NF-004 | TC-UX-01 | Partial |
| SAM-NF-005 | TC-DATA-01 | Partial |
| SAM-NF-006 | TC-AUDIT-01 | Pass |
| SAM-NF-007 | TC-SCALE-01 | Pass |
| SAM-SR-001 | TC-SEC-01 | Pass |
| SAM-SR-002 | TC-SEC-02 | Pass |
| SAM-SR-003 | TC-SEC-03 | Pass |
| SAM-SR-004 | TC-SEC-04 | Partial |
| SAM-SR-005 | TC-SEC-05 | Pass |

All 36 of the 36 requirements in the SRS have at least one test case. 33 are passing and 3 are partial: SAM-NF-005 (DEF-01), SAM-SR-004 (DEF-02) and SAM-NF-004 (manual usability trial not done).

## 5. Test data

Demo data comes from `python manage.py seed_demo`: admin, prof_smith, alice, bob and charlie, with subjects CS201 and CS301. Bob is a defaulter at 50% and charlie is at 100%. The unit tests make their own data in each test and use a temporary database, so they do not depend on each other.

## 6. Running the tests

    python manage.py test -v 2               (automated tests)
    python scripts/performance_test.py       (load test)
    python scripts/system_validation.py      (runs against a live server)
