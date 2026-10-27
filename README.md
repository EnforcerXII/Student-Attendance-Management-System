# Student Attendance Management System (SAMS)

A robust, role-based web application for tracking student attendance, calculating attendance metrics, identifying defaulters, generating reports, and maintaining immutable audit logs. Built with Python, Django, and modern responsive web standards.

---

## Features Implemented

### Sprint 1 Foundation
- **Role-Based Access Control (RBAC):** Distinct roles for `ADMIN`, `FACULTY`, and `STUDENT`.
- **Core Entities:** Custom user model, Students, Faculty, Subjects, Enrolments, and Attendance Sessions.
- **Attendance Marking:** Faculty can open class sessions and record attendance (Present / Late / Absent) with duplicate prevention.
- **CI Pipeline:** GitHub Actions workflow running automated linting and test execution on every commit/PR.

### Sprint 2 Capabilities
- **[ATT-02] Attendance Modification:** Authorized faculty can edit attendance records within their assigned subjects with reason tracking and audit logging (closes #14).
- **[VIEW-01] Student Portal:** Students can view their personal attendance records and comprehensive historical timelines (closes #16).
- **[VIEW-02] Faculty Dashboard:** Faculty can view assigned classes, subject metrics, and session archives (closes #17).
- **[CALC-01] Attendance Calculation & Defaulters:** Automatic subject-wise percentage calculation (`(Present + Late) / Total * 100`) and identification of students below the mandatory 75% threshold (closes #18).
- **[REP-01] Reports & CSV Export:** Comprehensive attendance reports filtered by subject, student, or date range, with one-click CSV export (closes #19).
- **[NOT-01] Low-Attendance Notifications:** Prominent warning banners on student dashboards when attendance falls below 75% (closes #20).
- **[NFR-03] Responsive UI:** Mobile-first, WCAG-conscious user interface with bulk actions ("Mark All Present") for rapid workflows (closes #21).
- **[NFR-01] Performance & Scalability:** Load-tested with 100 concurrent requests; p95 latency is 0.28s (< 3.0s threshold) with 0 errors (closes #23).
- **[NFR-02] Audit Logging:** Immutable activity logs capturing user, action, timestamp, entity, and old/new state values (closes #24).
- **[NFR-04] Health & Security:** `/health/` availability monitoring endpoint and HTTPS / secure proxy header configurations (closes #25).
- **[TEST-02] Test Suite & RTM:** 20 automated unit and integration tests passing with 100% coverage of Sprint 2 acceptance criteria (closes #27).
- **[DOC-02] Documentation & Freeze:** Sprint 2 completion report, deviation log, and video demo script (closes #29).

---

## Tech Stack
- **Backend:** Python 3.11+ / Django 5.2
- **Database:** MySQL 8 (Production) / SQLite (Automated testing & CI fallback)
- **Frontend:** Responsive HTML5, CSS3, JavaScript
- **Testing:** Django Test Framework, concurrent load testing script
- **CI/CD:** GitHub Actions

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/EnforcerXII/Student-Attendance-Management-System.git
   cd Student-Attendance-Management-System
   ```

2. **Set up virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://127.0.0.1:8000/`.

---

## Running Automated Tests

Run the complete test suite (20 tests covering all functional and non-functional requirements):
```bash
python manage.py test -v 2
```

Run the performance & scalability load test (100 concurrent requests):
```bash
python scripts/performance_test.py
```

---

## API & Endpoints Summary

| Endpoint | Method | Role | Description |
|---|---|---|---|
| `/health/` | GET | Public | System health check (`status`, `database`) |
| `/dashboard/` | GET | Authenticated | Role-directed dashboard with metrics and alerts |
| `/faculty/dashboard/` | GET | Faculty | Assigned subjects, stats, and quick links |
| `/attendance/subject/<id>/sessions/` | GET / POST | Faculty | View and create attendance sessions |
| `/attendance/sessions/<id>/mark/` | GET / POST | Faculty | Mark attendance with bulk actions |
| `/attendance/sessions/<id>/modify/` | GET / POST | Faculty | Permitted edit of session attendance with audit trail |
| `/attendance/report/<id>/` | GET | Faculty, Admin | Session report and student breakdown |
| `/attendance/my/` | GET | Student | Student attendance summary & full history |
| `/attendance/subject/<id>/defaulters/` | GET | Faculty, Admin | Low-attendance students (< 75%) |
| `/attendance/reports/` | GET | Faculty, Admin | Filterable reports with CSV export (`?format=csv`) |
| `/administration/audit-logs/` | GET | Admin | System audit trail |
| `/admin/` | GET / POST | Admin | Django administrative portal |

---

## Team & Credits
- **Product Owner / Team Lead:** Atul Kandiyil (PES2UG24CS920)
- **Dev Lead:** Riona Jeena Dsouza (PES2UG24CS654)
- **Test Engineer:** Amit (PES2UG24CS624)
- **QA Lead:** Shivakumar (PES2UG24CS548)
