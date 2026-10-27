# Sprint 2 Video Demo Script (2 Minutes)

**Topic:** Student Attendance Management System (SAMS) - Sprint 2 Features  
**Target Duration:** ~2 Minutes (120 seconds)  
**Deliverable for Issue #29 [DOC-02]**  

---

## Storyboard & Timing Breakdown

### [0:00 - 0:25] 1. Student Portal & Low-Attendance Alerts (Issues #16, #20)
- **Visual:** Log in as Student (`student2`).
- **Narration:**
  > "Welcome to the SAMS Sprint 2 demonstration. We begin on the Student Dashboard. Notice the prominent red notification banner alerting the student that their attendance in Data Structures is currently below the mandatory 75% threshold at 0%. Clicking 'View Detailed History' takes us to the dedicated Student Portal (`/attendance/my/`), displaying subject-wise totals, attendance percentages, and a complete chronological session timeline."

### [0:25 - 0:50] 2. Faculty Dashboard & Class Analytics (Issue #17)
- **Visual:** Log out, log in as Faculty (`faculty1`). Land on `/faculty/dashboard/`.
- **Narration:**
  > "Next, switching to the Faculty perspective. The dashboard displays all subjects assigned to this instructor. Each course card shows live stats: enrolled students, conducted sessions, overall attendance rate, and a highlighted count of defaulter students below the 75% threshold. From here, faculty can jump straight into session management, defaulters lists, or reports."

### [0:50 - 1:20] 3. Attendance Modification & Audit Logging (Issues #14, #21, #24)
- **Visual:** Navigate to Session Mark / Modify page (`/attendance/sessions/<id>/mark/`).
- **Narration:**
  > "Under Session Management, faculty can record or modify attendance. To streamline large cohorts, we've provided instant bulk actions: 'Mark All Present' and 'Mark All Absent' allow full rosters to be completed in one click. When updating an existing session, faculty can adjust individual statuses, provide an audit reason, and submit. Behind the scenes, our immutable AuditLog automatically records the instructor's ID, the previous status, the updated status, and the timestamp."

### [1:20 - 1:45] 4. Attendance Reports, Analytics & CSV Export (Issue #19)
- **Visual:** Open `/attendance/reports/`. Filter by subject, date range, or student. Click 'Export CSV'.
- **Narration:**
  > "The new Reports and Analytics module allows instructors and administrators to filter records by course, date range, or student name. Summary metric cards calculate live aggregate attendance percentages and status breakdowns. Clicking 'Export CSV' generates a clean, standardized spreadsheet download suitable for official institutional records."

### [1:45 - 2:00] 5. Health Check & Test Summary (Issues #23, #25, #27)
- **Visual:** Open `/health/` endpoint (shows JSON status: healthy, database: connected). Show terminal showing all 20 tests passing and load test completed.
- **Narration:**
  > "Finally, SAMS includes an automated `/health/` availability endpoint and security configurations. Our comprehensive test suite of 20 unit and integration tests passes with 100% success, and our 100-user concurrency test verifies sub-300ms response times. Sprint 2 is fully complete and frozen. Thank you!"

---

## Recording Checklist
- [ ] Browser window resolution set to 1920x1080 (16:9).
- [ ] Seed accounts ready:
  - Admin: `admin` / password
  - Faculty: `faculty1` / password
  - Student: `student2` (low attendance alert) / password
- [ ] Record voiceover or subtitles matching the timing markers.
- [ ] Export as MP4 and place under `demo/sprint2demo.mp4`.
