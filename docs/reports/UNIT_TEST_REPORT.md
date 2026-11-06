# Unit Test Report

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

This report covers the automated unit and integration tests for SAMS. They are run with Django's test runner (`python manage.py test`) and were run in the testing week as required by the Test Plan. The test cases they belong to are in the Test Case Document.

## 2. Summary

| | |
|---|---|
| Tests run | 83 |
| Passed | 81 |
| Expected failures | 2 |
| Unexpected failures or errors | 0 |
| Tests from Sprint 1 and 2 | 20 |
| Tests added in this round | 63 |
| Run time | about 1.6 seconds |

All 83 tests ran. 81 passed and nothing failed unexpectedly. The 2 expected failures are tests we wrote for two bugs found during this round (DEF-01 and DEF-02, described in the System Validation Report). We marked them with `@unittest.expectedFailure` so the GitHub Actions run stays green while the bugs are open. After the bugs are fixed these two will show as "unexpected success" and the decorator can be removed.

## 3. Results by module

| Module | Tests | Passed | Expected failures | Failed |
|---|---|---|---|---|
| accounts | 21 | 20 | 1 | 0 |
| administration | 12 | 12 | 0 | 0 |
| attendance | 50 | 49 | 1 | 0 |

## 4. Results by test class

| Test class | Tests | Passed | Expected failures | Failed |
|---|---|---|---|---|
| accounts.tests_auth.DashboardTests | 6 | 6 | 0 | 0 |
| accounts.tests_auth.LoginLogoutTests | 7 | 7 | 0 | 0 |
| accounts.tests_auth.PasswordAndTransportSecurityTests | 3 | 2 | 1 | 0 |
| accounts.tests_auth.RoleBasedAccessTests | 5 | 5 | 0 | 0 |
| administration.tests.EnrolmentConstraintTest | 1 | 1 | 0 | 0 |
| administration.tests.StudentModelTest | 1 | 1 | 0 | 0 |
| administration.tests_admin.AdminManagementTests | 10 | 10 | 0 | 0 |
| attendance.tests.AttendanceModelTest | 2 | 2 | 0 | 0 |
| attendance.tests.AttendanceWorkflowTests | 3 | 3 | 0 | 0 |
| attendance.tests.Sprint2Tests | 13 | 13 | 0 | 0 |
| attendance.tests_regression.HealthCheckFailureTests | 1 | 1 | 0 | 0 |
| attendance.tests_regression.MarkingTests | 11 | 10 | 1 | 0 |
| attendance.tests_regression.ModelAndServiceTests | 2 | 2 | 0 | 0 |
| attendance.tests_regression.ReportViewTests | 13 | 13 | 0 | 0 |
| attendance.tests_regression.SessionCreationTests | 5 | 5 | 0 | 0 |

## 5. Tests that are expected to fail

| Defect | Test | What happens |
|---|---|---|
| DEF-01 | attendance.tests_regression.MarkingTests.test_tc_data_01_partial_submission_is_rolled_back | One record is left in the database when 0 are expected |
| DEF-02 | accounts.tests_auth.PasswordAndTransportSecurityTests.test_tc_sec_04_secure_cookies_enabled | SESSION_COOKIE_SECURE is False because DEBUG is hard-coded to True |

## 6. All tests

| No. | Test | Result | Time (s) |
|---|---|---|---|
| 1 | accounts.tests_auth.DashboardTests.test_admin_dashboard_shows_totals | Pass | 0.028 |
| 2 | accounts.tests_auth.DashboardTests.test_faculty_dashboards_show_assigned_subjects_only | Pass | 0.014 |
| 3 | accounts.tests_auth.DashboardTests.test_student_dashboard_with_profile_and_records | Pass | 0.009 |
| 4 | accounts.tests_auth.DashboardTests.test_student_dashboard_without_attendance_records | Pass | 0.009 |
| 5 | accounts.tests_auth.DashboardTests.test_student_dashboard_without_student_profile | Pass | 0.007 |
| 6 | accounts.tests_auth.DashboardTests.test_user_str | Pass | 0.002 |
| 7 | accounts.tests_auth.LoginLogoutTests.test_tc_auth_01_login_page_renders | Pass | 0.003 |
| 8 | accounts.tests_auth.LoginLogoutTests.test_tc_auth_01_role_redirect_per_role | Pass | 0.021 |
| 9 | accounts.tests_auth.LoginLogoutTests.test_tc_auth_01_valid_login_creates_session | Pass | 0.004 |
| 10 | accounts.tests_auth.LoginLogoutTests.test_tc_auth_02_error_message_is_generic | Pass | 0.005 |
| 11 | accounts.tests_auth.LoginLogoutTests.test_tc_auth_02_invalid_password_rejected | Pass | 0.003 |
| 12 | accounts.tests_auth.LoginLogoutTests.test_tc_auth_02_unknown_user_rejected | Pass | 0.004 |
| 13 | accounts.tests_auth.LoginLogoutTests.test_tc_auth_04_logout_ends_session | Pass | 0.011 |
| 14 | accounts.tests_auth.PasswordAndTransportSecurityTests.test_tc_sec_03_password_is_hashed_not_plaintext | Pass | 0.761 |
| 15 | accounts.tests_auth.PasswordAndTransportSecurityTests.test_tc_sec_04_proxy_ssl_header_configured | Pass | 0.001 |
| 16 | accounts.tests_auth.PasswordAndTransportSecurityTests.test_tc_sec_04_secure_cookies_enabled | Expected fail | 0.002 |
| 17 | accounts.tests_auth.RoleBasedAccessTests.test_tc_auth_03_admin_allowed_on_admin_pages | Pass | 0.015 |
| 18 | accounts.tests_auth.RoleBasedAccessTests.test_tc_auth_03_faculty_blocked_from_student_and_admin_pages | Pass | 0.008 |
| 19 | accounts.tests_auth.RoleBasedAccessTests.test_tc_auth_03_student_blocked_from_faculty_and_admin_pages | Pass | 0.011 |
| 20 | accounts.tests_auth.RoleBasedAccessTests.test_tc_sec_01_unauthenticated_redirected_to_login | Pass | 0.005 |
| 21 | accounts.tests_auth.RoleBasedAccessTests.test_tc_sec_02_student_cannot_post_attendance_directly | Pass | 0.006 |
| 22 | administration.tests.EnrolmentConstraintTest.test_duplicate_student_subject_enrolment_is_rejected | Pass | 0.002 |
| 23 | administration.tests.StudentModelTest.test_student_creation | Pass | 0.001 |
| 24 | administration.tests_admin.AdminManagementTests.test_audit_log_view_lists_events_for_admin | Pass | 0.007 |
| 25 | administration.tests_admin.AdminManagementTests.test_model_string_representations | Pass | 0.005 |
| 26 | administration.tests_admin.AdminManagementTests.test_tc_enr_01_enrolled_student_appears_in_marking_list | Pass | 0.015 |
| 27 | administration.tests_admin.AdminManagementTests.test_tc_fac_01_admin_creates_faculty_who_can_login | Pass | 0.010 |
| 28 | administration.tests_admin.AdminManagementTests.test_tc_fac_02_assigned_faculty_sees_subject | Pass | 0.012 |
| 29 | administration.tests_admin.AdminManagementTests.test_tc_stu_01_admin_adds_student | Pass | 0.010 |
| 30 | administration.tests_admin.AdminManagementTests.test_tc_stu_01_duplicate_student_id_rejected | Pass | 0.006 |
| 31 | administration.tests_admin.AdminManagementTests.test_tc_stu_02_admin_updates_student | Pass | 0.011 |
| 32 | administration.tests_admin.AdminManagementTests.test_tc_stu_03_admin_lists_students | Pass | 0.026 |
| 33 | administration.tests_admin.AdminManagementTests.test_tc_sub_01_subject_created_and_code_unique | Pass | 0.004 |
| 34 | attendance.tests.AttendanceModelTest.test_attendance_creation | Pass | 0.002 |
| 35 | attendance.tests.AttendanceModelTest.test_duplicate_attendance_is_rejected | Pass | 0.002 |
| 36 | attendance.tests.AttendanceWorkflowTests.test_faculty_can_open_attendance_page | Pass | 0.008 |
| 37 | attendance.tests.AttendanceWorkflowTests.test_faculty_can_save_attendance | Pass | 0.013 |
| 38 | attendance.tests.AttendanceWorkflowTests.test_student_cannot_mark_attendance | Pass | 0.010 |
| 39 | attendance.tests.Sprint2Tests.test_tc_att_03_modify_attendance_permitted | Pass | 0.015 |
| 40 | attendance.tests.Sprint2Tests.test_tc_att_03_modify_attendance_unauthorized_blocked | Pass | 0.014 |
| 41 | attendance.tests.Sprint2Tests.test_tc_audit_01_and_sec_05_audit_logging | Pass | 0.021 |
| 42 | attendance.tests.Sprint2Tests.test_tc_calc_01_attendance_percentage_calculation | Pass | 0.004 |
| 43 | attendance.tests.Sprint2Tests.test_tc_calc_02_low_attendance_identification | Pass | 0.013 |
| 44 | attendance.tests.Sprint2Tests.test_tc_hist_01_student_attendance_history | Pass | 0.012 |
| 45 | attendance.tests.Sprint2Tests.test_tc_not_01_low_attendance_notification | Pass | 0.023 |
| 46 | attendance.tests.Sprint2Tests.test_tc_perf_01_response_time | Pass | 0.012 |
| 47 | attendance.tests.Sprint2Tests.test_tc_rel_01_health_check_endpoint | Pass | 0.003 |
| 48 | attendance.tests.Sprint2Tests.test_tc_rep_01_attendance_report_criteria | Pass | 0.017 |
| 49 | attendance.tests.Sprint2Tests.test_tc_rep_02_attendance_summaries_and_csv_export | Pass | 0.009 |
| 50 | attendance.tests.Sprint2Tests.test_tc_view_01_student_view_own_attendance_only | Pass | 0.016 |
| 51 | attendance.tests.Sprint2Tests.test_tc_view_02_faculty_view_assigned_classes_only | Pass | 0.012 |
| 52 | attendance.tests_regression.HealthCheckFailureTests.test_tc_rel_01_health_reports_503_when_database_down | Pass | 0.001 |
| 53 | attendance.tests_regression.MarkingTests.test_invalid_status_rejected_with_400 | Pass | 0.010 |
| 54 | attendance.tests_regression.MarkingTests.test_modification_without_reason_uses_default | Pass | 0.015 |
| 55 | attendance.tests_regression.MarkingTests.test_modify_view_shows_existing_values | Pass | 0.014 |
| 56 | attendance.tests_regression.MarkingTests.test_other_faculty_cannot_mark_or_modify | Pass | 0.010 |
| 57 | attendance.tests_regression.MarkingTests.test_tc_att_01_mark_all_statuses | Pass | 0.012 |
| 58 | attendance.tests_regression.MarkingTests.test_tc_att_03_modification_records_old_new_and_reason | Pass | 0.016 |
| 59 | attendance.tests_regression.MarkingTests.test_tc_att_04_resubmission_does_not_duplicate | Pass | 0.014 |
| 60 | attendance.tests_regression.MarkingTests.test_tc_data_01_database_blocks_duplicates | Pass | 0.003 |
| 61 | attendance.tests_regression.MarkingTests.test_tc_ux_01_bulk_marking_buttons_present | Pass | 0.009 |
| 62 | attendance.tests_regression.MarkingTests.test_unchanged_resubmission_writes_no_modification_audit | Pass | 0.014 |
| 63 | attendance.tests_regression.MarkingTests.test_tc_data_01_partial_submission_is_rolled_back | Expected fail | 0.010 |
| 64 | attendance.tests_regression.ModelAndServiceTests.test_attendance_and_session_str | Pass | 0.003 |
| 65 | attendance.tests_regression.ModelAndServiceTests.test_audit_log_anonymous_actor_and_strings | Pass | 0.003 |
| 66 | attendance.tests_regression.ReportViewTests.test_admin_sees_all_subjects_in_reports | Pass | 0.011 |
| 67 | attendance.tests_regression.ReportViewTests.test_defaulters_access_rules | Pass | 0.020 |
| 68 | attendance.tests_regression.ReportViewTests.test_defaulters_view_threshold_param | Pass | 0.024 |
| 69 | attendance.tests_regression.ReportViewTests.test_faculty_cannot_see_student_page | Pass | 0.008 |
| 70 | attendance.tests_regression.ReportViewTests.test_faculty_report_excludes_other_faculty_subjects | Pass | 0.012 |
| 71 | attendance.tests_regression.ReportViewTests.test_session_report_denied_for_other_faculty_and_student | Pass | 0.019 |
| 72 | attendance.tests_regression.ReportViewTests.test_session_report_for_faculty_and_admin | Pass | 0.025 |
| 73 | attendance.tests_regression.ReportViewTests.test_student_attendance_page_and_missing_profile | Pass | 0.022 |
| 74 | attendance.tests_regression.ReportViewTests.test_student_with_no_records_is_not_flagged | Pass | 0.006 |
| 75 | attendance.tests_regression.ReportViewTests.test_tc_calc_01_percentage_values | Pass | 0.004 |
| 76 | attendance.tests_regression.ReportViewTests.test_tc_calc_02_threshold_boundary | Pass | 0.008 |
| 77 | attendance.tests_regression.ReportViewTests.test_tc_rep_01_filters_subject_student_and_dates | Pass | 0.031 |
| 78 | attendance.tests_regression.ReportViewTests.test_tc_rep_02_summary_numbers_and_csv_match | Pass | 0.012 |
| 79 | attendance.tests_regression.SessionCreationTests.test_create_session_and_audit | Pass | 0.010 |
| 80 | attendance.tests_regression.SessionCreationTests.test_duplicate_session_not_created | Pass | 0.008 |
| 81 | attendance.tests_regression.SessionCreationTests.test_missing_date_rejected | Pass | 0.009 |
| 82 | attendance.tests_regression.SessionCreationTests.test_other_faculty_cannot_open_session_for_subject | Pass | 0.008 |
| 83 | attendance.tests_regression.SessionCreationTests.test_session_page_lists_sessions | Pass | 0.008 |

## 7. Notes

While `manage.py test` runs, the password hasher is switched to MD5 to keep the run fast (Deviation 3). The password tests switch it back to PBKDF2, and the System Validation Report checks the hashes stored in the real database as well.

The raw output is saved next to this report as `unit_test_results.xml` (JUnit format) and `unit_test_log.txt`.
