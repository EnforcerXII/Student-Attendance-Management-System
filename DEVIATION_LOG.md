# Sprint 2 Deviation Log

**Project:** Student Attendance Management System (SAMS)  
**Document Version:** 1.0  
**Date:** 27-Oct-2026  
**Authors:** Team 1 (Atul Kandiyil, Riona Jeena Dsouza, Amit, Shivakumar)  

---

## Purpose
This document logs all architectural, design, and implementation deviations between the initial specifications (SRS v1.0, SAD v1.0, STP v1.0) and the Sprint 2 delivered codebase. All deviations have been evaluated to ensure they enhance usability, performance, or developer experience without violating system requirements.

---

## Log of Deviations

### 1. Database Configuration Fallback
- **Initial Specification:** SAD Section 3.6 specified MySQL 8 (InnoDB) as the mandatory operational data store.
- **Implemented Architecture:** Dual-mode database configuration in `config/settings.py`. When `DB_NAME` is configured, MySQL is utilized with UTF-8 character encoding. If `DB_NAME` is absent or `GITHUB_ACTIONS=true`, the system gracefully falls back to SQLite (`db.sqlite3`).
- **Rationale:** Ensures zero-friction CI/CD pipeline runs and facilitates developer onboarding without requiring local MySQL server daemon setup for local automated unit testing.
- **Impact:** Positive. Production MySQL compatibility is preserved while maintaining seamless CI workflows.

### 2. In-Tree Automated Performance Test Script
- **Initial Specification:** STP Section 6 listed Apache JMeter for load and scalability testing.
- **Implemented Architecture:** In addition to supporting external HTTP load testing, an in-tree Python load tester (`scripts/performance_test.py`) was implemented using Python's `concurrent.futures.ThreadPoolExecutor`.
- **Rationale:** Enables fully automated, repeatable performance regression testing (100 concurrent requests, p95 calculation) directly in CI and local developer workstations without external JVM/JMeter dependencies.
- **Impact:** Positive. Provides immediate feedback on p95 latency and concurrent user capacity.

### 3. Password Hashing Fast-Path for Test Suite
- **Initial Specification:** SRS SAM-SR-003 and SAD Section 3.6 require strong salted password hashing (PBKDF2/Argon2).
- **Implemented Architecture:** Strong password hashing remains active in development and production environments. For `python manage.py test` invocations only (`if 'test' in sys.argv`), Django's `MD5PasswordHasher` is temporarily selected.
- **Rationale:** Reduces full test suite execution time from ~36 seconds to ~1.2 seconds, encouraging frequent local test execution.
- **Impact:** Neutral/Positive. Security standards are maintained for all runtime requests while accelerating the test cycle.

### 4. Bulk Marking Usability Actions
- **Initial Specification:** SRS Section 4.4 and SAD Section 4.5 specified individual dropdown selections per student.
- **Implemented Architecture:** Added client-side "Mark All Present" and "Mark All Absent" shortcut buttons in `mark_attendance.html`.
- **Rationale:** Allows faculty teaching large cohorts (e.g., 60-80 students) to mark attendance with a single click and review exceptions, easily meeting the sub-3-second completion target (SAM-NF-004, TC-UX-01).
- **Impact:** High positive usability improvement.

### 5. Architectural Cohesion of Audit Log Model
- **Initial Specification:** SAD Section 3.4 conceptualized `AuditService` as an independent library.
- **Implemented Architecture:** Implemented `AuditLog` entity in `attendance/models.py` with an immutable append-only pattern, exposed via `attendance/services.py` (`log_audit_event`), and registered in Django admin as well as a dedicated `/administration/audit-logs/` dashboard.
- **Rationale:** Aligns with Django's modular monolith conventions, ensuring transactional integrity with attendance operations within the same database transaction.
- **Impact:** Positive. Simplifies audit data querying and eliminates inter-service distributed transaction overhead.

---

## Summary Assessment
All recorded deviations have been reviewed and approved by the team leads. No functional gaps exist relative to the SRS v1.0 specifications.
