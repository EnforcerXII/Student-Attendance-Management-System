# System Validation Report

Student Attendance Management System (SAMS)

| | |
|---|---|
| Project | Student Attendance Management System (SAMS) |
| Version | 1.0 |
| Authors | Atul Kandiyil (PES2UG24CS920), Riona Jeena Dsouza (PES2UG24CS654), Amit (PES2UG24CS624) - Team 1 |
| Date | 06-11-2026 |
| Build tested | main branch, commit 33cdb28, plus the new test files |
| Environment | Python 3.12.3, Django 5.2.18, SQLite, Linux |

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 06-11-2026 | Team 1 | First version. |

## Approvals

| Role | Name | Signature / Date |
|---|---|---|
| Team Lead | Atul Kandiyil | |
| Dev Lead | Riona Jeena Dsouza | |
| Test Engineer | Amit | |

## 1. Introduction

System validation checks the finished system as a user would see it. For this we did not use the Django test client. The script `scripts/system_validation.py` sets up a fresh database, loads the demo data, starts the real server and then logs in as admin, faculty and student over HTTP, with cookies and CSRF tokens like a browser. After each step it checks the response, and for some steps it also looks directly in the database. The scenarios cover the SRS acceptance criteria and the system testing level of the Test Plan.

## 2. Results

22 of the 24 scenarios passed. The two that failed are caused by the defects in section 4.

| ID | Scenario | Requirement / test case | Result | Evidence |
|---|---|---|---|---|
| SV-01 | Health endpoint reports healthy | SAM-NF-002 / TC-REL-01 | Pass | HTTP 200 {'status': 'healthy', 'database': 'connected'} |
| SV-02 | Anonymous user redirected to login | SAM-SR-001 / TC-SEC-01 | Pass | HTTP 302 -> /accounts/login/?next=/dashboard/ |
| SV-03 | Invalid login rejected, no session | SAM-F-002 / TC-AUTH-02 | Pass | HTTP 200, session cookie issued: False |
| SV-04 | Student logs in and lands on dashboard | SAM-F-001 / TC-AUTH-01 | Pass | final URL http://127.0.0.1:8765/dashboard/, HTTP 200 |
| SV-05 | Student sees own attendance with low-attendance alert (bob, 50%) | SAM-F-017, F-018, F-023, F-024 / TC-VIEW-01, TC-CALC-01, TC-NOT-01, TC-HIST-01 | Pass | HTTP 200, alert banner present: True |
| SV-06 | Student with good attendance sees no alert (charlie, 100%) | SAM-F-023 / TC-NOT-01 | Pass | HTTP 200, banner absent |
| SV-07 | Student blocked from faculty/admin pages (403) | SAM-F-003, SAM-SR-002 / TC-AUTH-03, TC-SEC-02 | Pass | {'/faculty/dashboard/': 403, '/attendance/reports/': 403, '/administration/audit-logs/': 403} |
| SV-08 | Student cannot mark attendance by direct POST | SAM-F-013 / TC-ATT-02 | Pass | HTTP 403 |
| SV-09 | Faculty dashboard shows assigned subjects | SAM-F-019 / TC-VIEW-02 | Pass | HTTP 200 |
| SV-10 | Faculty creates a session; same date twice does not duplicate | SAM-F-012, F-015 / TC-ATT-01, TC-ATT-04 | Pass | 1 session row(s) for 2026-11-20 |
| SV-11 | Faculty marks Present/Absent/Late for all enrolled students | SAM-F-012, F-016 / TC-ATT-01, TC-ATT-05 | Pass | HTTP 302, 3/3 records saved |
| SV-12 | Re-submitting the same sheet creates no duplicates | SAM-F-015 / TC-ATT-04 | Pass | 3 records after second submit |
| SV-13 | Faculty modifies a record; old/new value and reason audited | SAM-F-014, SAM-NF-006 / TC-ATT-03, TC-AUDIT-01 | Pass | status now PRESENT, audit row ('ABSENT', 'PRESENT', 'System test correction') |
| SV-14 | Defaulters list flags students below 75% | SAM-F-020 / TC-CALC-02 | Pass | HTTP 200, STU102 (bob) listed: True |
| SV-15 | Report filters and CSV export work | SAM-F-021, F-022 / TC-REP-01, TC-REP-02 | Pass | HTTP 200, CSV rows (excl. header): 5 |
| SV-16 | Invalid attendance status rejected | Input validation (STP 5.1) / TC-ATT | Pass | HTTP 400 |
| SV-17 | Admin dashboard shows system totals | SAM-F-003 (admin role) | Pass | HTTP 200 |
| SV-18 | Admin can view audit log containing the correction | SAM-NF-006, SAM-SR-005 / TC-AUDIT-01, TC-SEC-05 | Pass | HTTP 200 |
| SV-19 | Admin portal manages students/faculty/subjects/enrolments | SAM-F-005..F-011 / TC-STU, TC-FAC, TC-SUB, TC-ENR | Pass | HTTP 200 |
| SV-20 | Logout ends the session | SAM-F-004 / TC-AUTH-04 | Pass | logout HTTP 302; dashboard then HTTP 302 |
| SV-21 | Stored passwords are salted one-way hashes (runtime hasher) | SAM-SR-003 / TC-SEC-03 | Pass | 5 users; scheme(s): ['pbkdf2_sha256'] |
| SV-22 | Session and CSRF cookies carry the Secure flag | SAM-SR-004 / TC-SEC-04 | Fail | cookie Secure flags: {'csrftoken': False, 'sessionid': False, 'messages': False}  (see DEF-02) |
| SV-23 | Rejected submission leaves no partial records | SAM-NF-005 / TC-DATA-01 | Fail | HTTP 400, 1 record(s) left behind (see DEF-01) |
| SV-24 | 100 concurrent logged-in users view their attendance; p95 <= 3 s | SAM-NF-001, SAM-NF-007 / TC-PERF-01, TC-SCALE-01 | Pass | 100 workers, errors=0, avg=0.220s p95=0.593s max=1.059s |

## 3. Performance and scalability

`scripts/performance_test.py` sends 100 requests to the reports page with a concurrency of 10:

    Total Requests: 100 | Concurrency: 10
    Total Duration:     1.75 s
    Requests Completed: 100 (Success: 100, Failed: 0)
    Throughput:         57.3 req/s
    Average Latency:    0.0415 s
    Median (p50):       0.0248 s
    90th percentile:    0.0931 s
    95th percentile:    0.1616 s
    99th percentile:    0.2179 s
    Max Latency:        0.2179 s
    [TC-PERF-01] 95th percentile <= 3.0s: PASSED (0.1616s)
    [TC-SCALE-01] 100 concurrent requests without failure: PASSED (0 errors)

Scenario SV-24 is the stricter test: 100 logged-in users hitting the server at the same time. The result is in the table above.

## 4. Defects found

### DEF-01 (Medium severity), SAM-NF-005, TC-DATA-01

If a marking form is submitted with an invalid status for one student, the server answers 400 but the records already saved for earlier students in the same request stay in the database. mark_attendance returns the 400 response from inside transaction.atomic() instead of raising, so nothing gets rolled back.

How we found it: Post a form where student 1 is PRESENT and student 2 is BOGUS. We got HTTP 400 and one record left behind (scenario SV-23).

Suggested fix: Check every submitted status before saving anything, or raise inside the atomic block.

Status: Open

### DEF-02 (High severity), SAM-SR-004, TC-SEC-04

settings.py has DEBUG = True written in directly, so the block under 'if not DEBUG' (secure session and CSRF cookies, X_FRAME_OPTIONS and so on) never runs. SECRET_KEY is also a fixed key that is committed to the repo.

How we found it: Log in on the running server and look at the cookies: sessionid and csrftoken have no Secure flag (scenario SV-22).

Suggested fix: Read DEBUG, SECRET_KEY and ALLOWED_HOSTS from environment variables (.env is already in .gitignore) and make DEBUG default to False.

Status: Open

## 5. Other observations

OBS-01: scripts/performance_test.py sends 100 requests with a concurrency of 10, not 100 users at the same time, although the README calls it 100 concurrent requests. Scenario SV-24 covers this properly with 100 simultaneous logged-in users against the running server (0 errors).

OBS-02: A few things in the SAD are not in the SRS and are not built: the 48-hour correction window (any assigned faculty can modify a record at any time), lockout after 5 failed logins, QR and biometric capture, and the JWT API. We did not test them because the SRS and Test Plan do not ask for them. They are not in DEVIATION_LOG.md yet and should be added.

OBS-03: All automated tests ran on SQLite, the CI fallback from Deviation 1. MySQL 8 is the target in the Test Plan and was not available, so it has not been tested.

OBS-04: Student, faculty, subject and enrolment management (SAM-F-005 to F-011) only exists in the Django admin portal. The portal has no search box set up, so SAM-F-007 is covered by the admin list and by the student filter on the reports page.

OBS-05: Not done in this round: the manual usability trial with real users (TC-UX-01), screen reader / WCAG checks, other browsers and mobile, and an HTTPS check on a deployed server.

## 6. SRS acceptance criteria (SRS section 6.3)

| No. | Criterion | Result | Reason |
|---|---|---|---|
| 1 | All 24 functional requirements implemented and tested | Met | All 24 have test cases and pass |
| 2 | All 7 non-functional requirements meet their criteria | Partly met | NF-001, 002, 003, 006 and 007 pass. NF-005 has DEF-01. NF-004 still needs the manual usability trial |
| 3 | The 2 security objectives are satisfied | Mostly met | Access control and audit work. Transport hardening is open (DEF-02) |
| 4 | All 5 security requirements pass their tests | Partly met | SR-001, 002, 003 and 005 pass. SR-004 is open (DEF-02) |
| 5 | Role-based access separates Admin, Faculty and Student | Met | SV-07, SV-08 and the unit tests |
| 6 | Attendance records and percentages are accurate | Met | TC-CALC-01, TC-CALC-02, SV-05, SV-14 |
| 7 | Required reports can be generated | Met | TC-REP-01, TC-REP-02, SV-15 |
| 8 | No critical defects remain | Met | No critical defects. One high (DEF-02) and one medium (DEF-01) are open |

## 7. Exit criteria and conclusion

The Test Plan asks for three things before testing can be closed.

1. All planned test cases executed. All 35 test cases were run in the automated tests or on the live system. The exception is the manual usability trial for TC-UX-01 and a check on a deployed HTTPS server (OBS-05).
2. No critical defects open. This is true, there are none.
3. Acceptance criteria met or formally accepted. This is not done yet. DEF-02 and DEF-01 are still open and need to be fixed or accepted by the Team Lead.

We plan to fix DEF-02 (a few lines in settings.py) and DEF-01 (validate before saving) and then run `python manage.py test` again. After that the two expected-failure tests should show as unexpected successes and their decorators can be removed.
