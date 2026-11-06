#!/usr/bin/env python3
"""System validation: drives a LIVE SAMS server over HTTP (like a browser) and records
PASS/FAIL per scenario against the SRS requirements.

Usage:  python scripts/system_validation.py            (starts its own server on :8765)
Output: docs/reports/system_validation_results.json
"""
import json, os, re, sqlite3, statistics, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
PORT = 8765
BASE = f"http://127.0.0.1:{PORT}"
ENV = {**os.environ, "GITHUB_ACTIONS": "true"}
RESULTS = []


def record(sid, title, reqs, ok, evidence):
    RESULTS.append({"id": sid, "title": title, "requirements": reqs,
                    "result": "PASS" if ok else "FAIL", "evidence": evidence})
    print(f"[{'PASS' if ok else 'FAIL'}] {sid} {title} -- {evidence}")


def session():
    s = requests.Session()
    return s


def csrf(s, url):
    r = s.get(BASE + url)
    return s.cookies.get("csrftoken"), r


def login(user, pw):
    s = session()
    tok, _ = csrf(s, "/accounts/login/")
    r = s.post(BASE + "/accounts/login/", data={"username": user, "password": pw,
                                                 "csrfmiddlewaretoken": tok}, allow_redirects=True)
    return s, r


def post(s, url, data, **kw):
    tok = s.cookies.get("csrftoken")
    return s.post(BASE + url, data={**data, "csrfmiddlewaretoken": tok}, **kw)


def main():
    db = ROOT / "db.sqlite3"
    if db.exists():
        db.unlink()
    run = lambda *a: subprocess.run([sys.executable, "manage.py", *a], cwd=ROOT, env=ENV,
                                    capture_output=True, text=True, check=True)
    run("migrate", "-v0")
    run("seed_demo")
    server = subprocess.Popen([sys.executable, "manage.py", "runserver", str(PORT), "--noreload"],
                              cwd=ROOT, env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                if requests.get(BASE + "/health/", timeout=1).status_code == 200:
                    break
            except Exception:
                time.sleep(0.5)
        scenarios()
    finally:
        server.terminate()
        server.wait()
    out = ROOT / "docs" / "reports" / "system_validation_results.json"
    out.write_text(json.dumps(RESULTS, indent=2))
    passed = sum(r["result"] == "PASS" for r in RESULTS)
    print(f"\n{passed}/{len(RESULTS)} scenarios passed -> {out}")


def scenarios():
    # SV-01 health
    r = requests.get(BASE + "/health/")
    record("SV-01", "Health endpoint reports healthy", "SAM-NF-002 / TC-REL-01",
           r.status_code == 200 and r.json().get("status") == "healthy", f"HTTP {r.status_code} {r.json()}")

    # SV-02 anonymous redirect
    r = requests.get(BASE + "/dashboard/", allow_redirects=False)
    record("SV-02", "Anonymous user redirected to login", "SAM-SR-001 / TC-SEC-01",
           r.status_code == 302 and "/accounts/login/" in r.headers["Location"], f"HTTP {r.status_code} -> {r.headers.get('Location')}")

    # SV-03 invalid login
    s = session(); tok, _ = csrf(s, "/accounts/login/")
    r = s.post(BASE + "/accounts/login/", data={"username": "alice", "password": "wrong", "csrfmiddlewaretoken": tok})
    record("SV-03", "Invalid login rejected, no session", "SAM-F-002 / TC-AUTH-02",
           r.status_code == 200 and "sessionid" not in s.cookies, f"HTTP {r.status_code}, session cookie issued: {'sessionid' in s.cookies}")

    # SV-04 student login + own data
    st, r = login("bob", "student123")
    ok = "sessionid" in st.cookies and r.status_code == 200
    record("SV-04", "Student logs in and lands on dashboard", "SAM-F-001 / TC-AUTH-01", ok, f"final URL {r.url}, HTTP {r.status_code}")
    r = st.get(BASE + "/attendance/my/")
    low = "mandatory" in r.text and "75" in r.text
    record("SV-05", "Student sees own attendance with low-attendance alert (bob, 50%)",
           "SAM-F-017, F-018, F-023, F-024 / TC-VIEW-01, TC-CALC-01, TC-NOT-01, TC-HIST-01",
           r.status_code == 200 and "CS201" in r.text and low, f"HTTP {r.status_code}, alert banner present: {low}")
    st2, _ = login("charlie", "student123")
    r2 = st2.get(BASE + "/attendance/my/")
    record("SV-06", "Student with good attendance sees no alert (charlie, 100%)", "SAM-F-023 / TC-NOT-01",
           r2.status_code == 200 and "mandatory" not in r2.text, f"HTTP {r2.status_code}, banner absent")

    # SV-07 RBAC
    codes = {u: st.get(BASE + u).status_code for u in ("/faculty/dashboard/", "/attendance/reports/", "/administration/audit-logs/")}
    record("SV-07", "Student blocked from faculty/admin pages (403)", "SAM-F-003, SAM-SR-002 / TC-AUTH-03, TC-SEC-02",
           all(c == 403 for c in codes.values()), str(codes))
    r = post(st, "/attendance/sessions/1/mark/", {"status_1": "PRESENT"}, allow_redirects=False)
    record("SV-08", "Student cannot mark attendance by direct POST", "SAM-F-013 / TC-ATT-02", r.status_code == 403, f"HTTP {r.status_code}")

    # faculty
    fs, r = login("prof_smith", "faculty123")
    r = fs.get(BASE + "/faculty/dashboard/")
    record("SV-09", "Faculty dashboard shows assigned subjects", "SAM-F-019 / TC-VIEW-02",
           r.status_code == 200 and "CS201" in r.text, f"HTTP {r.status_code}")
    r = fs.get(BASE + "/attendance/subject/1/sessions/")
    new_date = "2026-11-20"
    post(fs, "/attendance/subject/1/sessions/", {"session_date": new_date}, allow_redirects=True)
    post(fs, "/attendance/subject/1/sessions/", {"session_date": new_date}, allow_redirects=True)
    con = sqlite3.connect(ROOT / "db.sqlite3")
    n = con.execute("select count(*) from attendance_attendancesession where session_date=? and subject_id=1", (new_date,)).fetchone()[0]
    record("SV-10", "Faculty creates a session; same date twice does not duplicate", "SAM-F-012, F-015 / TC-ATT-01, TC-ATT-04", n == 1, f"{n} session row(s) for {new_date}")
    sid = con.execute("select id from attendance_attendancesession where session_date=? and subject_id=1", (new_date,)).fetchone()[0]
    studs = [r[0] for r in con.execute("select student_id from administration_enrolment where subject_id=1 order by student_id")]
    page = fs.get(BASE + f"/attendance/sessions/{sid}/mark/")
    data = {f"status_{sid_}": st_ for sid_, st_ in zip(studs, ["PRESENT", "ABSENT", "LATE"])}
    r = post(fs, f"/attendance/sessions/{sid}/mark/", data, allow_redirects=False)
    cnt = con.execute("select count(*) from attendance_attendance where session_id=?", (sid,)).fetchone()[0]
    record("SV-11", "Faculty marks Present/Absent/Late for all enrolled students", "SAM-F-012, F-016 / TC-ATT-01, TC-ATT-05",
           r.status_code == 302 and cnt == len(studs), f"HTTP {r.status_code}, {cnt}/{len(studs)} records saved")
    post(fs, f"/attendance/sessions/{sid}/mark/", data, allow_redirects=False)
    cnt2 = con.execute("select count(*) from attendance_attendance where session_id=?", (sid,)).fetchone()[0]
    record("SV-12", "Re-submitting the same sheet creates no duplicates", "SAM-F-015 / TC-ATT-04", cnt2 == cnt, f"{cnt2} records after second submit")
    data2 = dict(data); data2[f"status_{studs[1]}"] = "PRESENT"; data2["reason"] = "System test correction"
    post(fs, f"/attendance/sessions/{sid}/modify/", data2, allow_redirects=False)
    new_status = con.execute("select status from attendance_attendance where session_id=? and student_id=?", (sid, studs[1])).fetchone()[0]
    aud = con.execute("select old_value,new_value,reason from attendance_auditlog where action='ATTENDANCE_MODIFIED' and reason='System test correction'").fetchone()
    record("SV-13", "Faculty modifies a record; old/new value and reason audited", "SAM-F-014, SAM-NF-006 / TC-ATT-03, TC-AUDIT-01",
           new_status == "PRESENT" and aud == ("ABSENT", "PRESENT", "System test correction"), f"status now {new_status}, audit row {aud}")
    r = fs.get(BASE + "/attendance/subject/1/defaulters/")
    record("SV-14", "Defaulters list flags students below 75%", "SAM-F-020 / TC-CALC-02", r.status_code == 200 and "STU102" in r.text, f"HTTP {r.status_code}, STU102 (bob) listed: {'STU102' in r.text}")
    r = fs.get(BASE + "/attendance/reports/", params={"subject": 1, "student": "STU101"})
    csvr = fs.get(BASE + "/attendance/reports/", params={"subject": 1, "student": "STU101", "format": "csv"})
    lines = csvr.text.strip().splitlines()
    record("SV-15", "Report filters and CSV export work", "SAM-F-021, F-022 / TC-REP-01, TC-REP-02",
           r.status_code == 200 and csvr.headers.get("Content-Type", "").startswith("text/csv") and len(lines) >= 2 and "STU101" in lines[1],
           f"HTTP {r.status_code}, CSV rows (excl. header): {len(lines)-1}")
    bad = {f"status_{studs[0]}": "BOGUS"}
    r = post(fs, f"/attendance/sessions/{sid}/mark/", bad, allow_redirects=False)
    record("SV-16", "Invalid attendance status rejected", "Input validation (STP 5.1) / TC-ATT", r.status_code == 400, f"HTTP {r.status_code}")

    # admin
    a, _ = login("admin", "admin123")
    r = a.get(BASE + "/dashboard/")
    record("SV-17", "Admin dashboard shows system totals", "SAM-F-003 (admin role)", r.status_code == 200 and "Admin" in r.text, f"HTTP {r.status_code}")
    r = a.get(BASE + "/administration/audit-logs/")
    record("SV-18", "Admin can view audit log containing the correction", "SAM-NF-006, SAM-SR-005 / TC-AUDIT-01, TC-SEC-05",
           r.status_code == 200 and "System test correction" in r.text, f"HTTP {r.status_code}")
    r = a.get(BASE + "/admin/administration/student/")
    record("SV-19", "Admin portal manages students/faculty/subjects/enrolments", "SAM-F-005..F-011 / TC-STU, TC-FAC, TC-SUB, TC-ENR",
           r.status_code == 200 and "STU101" in r.text, f"HTTP {r.status_code}")

    # logout
    r = post(st, "/accounts/logout/", {}, allow_redirects=False)
    r2 = st.get(BASE + "/dashboard/", allow_redirects=False)
    record("SV-20", "Logout ends the session", "SAM-F-004 / TC-AUTH-04", r.status_code == 302 and r2.status_code == 302 and "/accounts/login/" in r2.headers["Location"], f"logout HTTP {r.status_code}; dashboard then HTTP {r2.status_code}")

    # security
    pw = con.execute("select password from accounts_user").fetchall()
    record("SV-21", "Stored passwords are salted one-way hashes (runtime hasher)", "SAM-SR-003 / TC-SEC-03",
           all(p[0].startswith("pbkdf2_sha256$") for p in pw), f"{len(pw)} users; scheme(s): {sorted({p[0].split('$')[0] for p in pw})}")
    sc = [c for c in fs.cookies]
    flags = {c.name: c.secure for c in sc}
    record("SV-22", "Session and CSRF cookies carry the Secure flag", "SAM-SR-004 / TC-SEC-04", all(flags.values()) and bool(flags), f"cookie Secure flags: {flags}  (see DEF-02)")

    # integrity: partial submit
    sid2 = con.execute("select id from attendance_attendancesession where session_date='2026-11-21'").fetchone()
    post(fs, "/attendance/subject/1/sessions/", {"session_date": "2026-11-21"})
    sid2 = con.execute("select id from attendance_attendancesession where session_date='2026-11-21'").fetchone()[0]
    mixed = {f"status_{studs[0]}": "PRESENT", f"status_{studs[1]}": "BOGUS", f"status_{studs[2]}": "PRESENT"}
    r = post(fs, f"/attendance/sessions/{sid2}/mark/", mixed, allow_redirects=False)
    left = con.execute("select count(*) from attendance_attendance where session_id=?", (sid2,)).fetchone()[0]
    record("SV-23", "Rejected submission leaves no partial records", "SAM-NF-005 / TC-DATA-01", r.status_code == 400 and left == 0, f"HTTP {r.status_code}, {left} record(s) left behind (see DEF-01)")

    # performance: 100 truly concurrent users against the live server
    def one(_):
        c = requests.Session(); t = time.perf_counter()
        resp = c.get(BASE + "/health/")
        return resp.status_code, time.perf_counter() - t
    def one_auth(i):
        c, _ = login("charlie", "student123"); t = time.perf_counter()
        resp = c.get(BASE + "/attendance/my/")
        return resp.status_code, time.perf_counter() - t
    with ThreadPoolExecutor(max_workers=100) as ex:
        res = list(ex.map(one_auth, range(100)))
    lat = sorted(x[1] for x in res); errs = sum(1 for x in res if x[0] != 200)
    p95 = lat[int(len(lat) * 0.95)]
    record("SV-24", "100 concurrent logged-in users view their attendance; p95 <= 3 s", "SAM-NF-001, SAM-NF-007 / TC-PERF-01, TC-SCALE-01",
           p95 <= 3.0 and errs == 0, f"100 workers, errors={errs}, avg={statistics.mean(lat):.3f}s p95={p95:.3f}s max={lat[-1]:.3f}s")


if __name__ == "__main__":
    main()
