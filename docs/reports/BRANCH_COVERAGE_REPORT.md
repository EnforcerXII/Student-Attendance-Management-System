# Branch Coverage Report

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

Branch coverage counts the outcomes of every decision in the code (both the true and the false side of each if, for example). It is stricter than line coverage. It was measured with coverage.py using `branch = True` in `.coveragerc`.

## 2. Summary

| | |
|---|---|
| Branches | 72 |
| Covered | 69 (95.8%) |
| Missed | 3 |
| Decisions only partly covered | 3 |

All the business code is fully covered: the views in `accounts`, `administration` and `attendance`, and `attendance/services.py` have no missed branches. The 3 missed branches are all in `config/settings.py`.

## 3. Branch coverage by file

Files with no decisions (models, admin, urls) are not listed.

| File | Branches | Covered | Missed | Partial | Coverage |
|---|---|---|---|---|---|
| accounts/views.py | 10 | 10 | 0 | 0 | 100% |
| administration/views.py | 2 | 2 | 0 | 0 | 100% |
| attendance/services.py | 6 | 6 | 0 | 0 | 100% |
| attendance/views.py | 48 | 48 | 0 | 0 | 100% |
| config/settings.py | 6 | 3 | 3 | 3 | 50% |

## 4. Branches not covered

| Line | Decision | Why the other side is never taken |
|---|---|---|
| settings.py, 84 to 92 | SQLite fallback or MySQL | The tests always use the SQLite fallback, no MySQL server (OBS-03) |
| settings.py, 125 to 134 | "test" in sys.argv is false | Settings are loaded by the test runner here. The real password hasher is checked on the live database in SV-21 |
| settings.py, 161 to 162 | "if not DEBUG" is true | DEBUG is hard-coded to True (DEF-02) |

## 5. What the tests exercise

Some of the decisions that the new tests cover:

- Marking attendance: a valid or an invalid status, a record that already exists and changed, one that exists and did not change, and a new record. The reason is either given or defaults.
- The reports page: each filter (subject, start date, end date, student) on and off, CSV or normal page, faculty or admin.
- The defaulters list: a valid threshold and an invalid one, faculty and admin.
- Every view that checks the role: allowed, refused, owner and not owner.
- Percentage: zero classes and non-zero classes, and a student at exactly the threshold.
- The health check with the database up and down.
