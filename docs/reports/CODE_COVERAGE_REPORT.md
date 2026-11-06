# Code Coverage Report

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

This report shows how much of the SAMS source code is run by the automated tests. It was measured with coverage.py 7.17.2. The settings are in `.coveragerc` in the root of the repo.

The measurement covers the four packages `accounts`, `administration`, `attendance` and `config`. We left out migrations, the test files, manage.py, the wsgi/asgi files, the `scripts` folder and the `seed_demo` demo command. The demo command is used in the system validation run but not by the unit tests.

## 2. Summary

| | |
|---|---|
| Statements | 428 |
| Covered | 422 (98.6%) |
| Missed | 6 |
| Statement and branch coverage combined | 98.2% |
| Tests run | 83 |

Before this round coverage was 83% with 20 tests. With the 83 tests it is now 98%. Every file in `accounts`, `administration` and `attendance` is at 100%.

## 3. Coverage by file

| File | Statements | Missed | Covered | Missing lines |
|---|---|---|---|---|
| accounts/__init__.py | 0 | 0 | 100% | - |
| accounts/admin.py | 7 | 0 | 100% | - |
| accounts/apps.py | 4 | 0 | 100% | - |
| accounts/models.py | 10 | 0 | 100% | - |
| accounts/urls.py | 3 | 0 | 100% | - |
| accounts/views.py | 55 | 0 | 100% | - |
| administration/__init__.py | 0 | 0 | 100% | - |
| administration/admin.py | 6 | 0 | 100% | - |
| administration/apps.py | 4 | 0 | 100% | - |
| administration/models.py | 29 | 0 | 100% | - |
| administration/urls.py | 3 | 0 | 100% | - |
| administration/views.py | 10 | 0 | 100% | - |
| attendance/__init__.py | 0 | 0 | 100% | - |
| attendance/admin.py | 10 | 0 | 100% | - |
| attendance/apps.py | 4 | 0 | 100% | - |
| attendance/models.py | 40 | 0 | 100% | - |
| attendance/services.py | 45 | 0 | 100% | - |
| attendance/urls.py | 3 | 0 | 100% | - |
| attendance/views.py | 147 | 0 | 100% | - |
| config/__init__.py | 0 | 0 | 100% | - |
| config/settings.py | 36 | 6 | 83% | 92, 162, 163, 164, 165, 166 |
| config/urls.py | 12 | 0 | 100% | - |

## 4. What is not covered

All the missed lines are in the config package.

| Location | What it is | Why it is not covered |
|---|---|---|
| config/settings.py, line 92 | The MySQL DATABASES setting | The tests run on SQLite and no MySQL server was available (OBS-03) |
| config/settings.py, lines 162 to 166 | The "if not DEBUG" block with the secure cookie settings | DEBUG is hard-coded to True so this block can never run. This is DEF-02 |

## 5. Files

Open `docs/reports/coverage_html/index.html` in a browser to see every line highlighted. The same data is in `coverage.xml` and `coverage.json`.
