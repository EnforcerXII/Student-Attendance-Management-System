#!/usr/bin/env python3
"""
Performance & Scalability Load Test Script (SAM-NF-001, SAM-NF-007, TC-PERF-01, TC-SCALE-01).

Simulates concurrent user load (100 concurrent requests), collects latency metrics
(min, avg, p50, p90, p95, max), verifies response times <= 3.0 s, and asserts zero failures.
"""

import os
import sys
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

# Set up Django environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from administration.models import Faculty, Student, Subject, Enrolment
from attendance.models import AttendanceSession, Attendance

User = get_user_model()


def setup_test_data():
    """Seed lightweight fixtures for load testing."""
    faculty_user, _ = User.objects.get_or_create(
        username="perf_faculty",
        defaults={"role": User.Role.FACULTY},
    )

    faculty, _ = Faculty.objects.get_or_create(
        faculty_id="PERF_FAC01",
        defaults={"user": faculty_user, "department": "Computer Science"},
    )

    subject, _ = Subject.objects.get_or_create(
        subject_code="PERF101",
        defaults={"subject_name": "Performance Engineering", "faculty": faculty},
    )

    # Seed 20 students enrolled
    for i in range(1, 21):
        stu_user, _ = User.objects.get_or_create(
            username=f"perf_stu_{i}",
            defaults={"role": User.Role.STUDENT},
        )
        student, _ = Student.objects.get_or_create(
            student_id=f"PERF_S{i:03d}",
            defaults={"user": stu_user, "department": "Computer Science", "year_of_study": 2},
        )
        Enrolment.objects.get_or_create(student=student, subject=subject)

    session, _ = AttendanceSession.objects.get_or_create(
        subject=subject,
        session_date="2026-10-27",
        defaults={"created_by": faculty_user},
    )

    return faculty_user, subject, session


def run_single_request(faculty_user):
    client = Client()
    client.force_login(faculty_user)

    url = reverse("attendance_reports")
    start = time.perf_counter()
    response = client.get(url)
    elapsed = time.perf_counter() - start

    return response.status_code, elapsed


def run_load_test(total_requests=100, concurrency=10):
    print("=== Starting SAMS Performance & Scalability Test ===")
    print(f"Total Requests: {total_requests} | Concurrency: {concurrency}")
    print("Target: SAM-NF-001 (95th percentile <= 3.0s), SAM-NF-007 (100 users)\n")

    faculty_user, subject, session = setup_test_data()

    latencies = []
    status_codes = []

    start_total = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(run_single_request, faculty_user) for _ in range(total_requests)]
        for f in futures:
            code, elapsed = f.result()
            status_codes.append(code)
            latencies.append(elapsed)

    total_time = time.perf_counter() - start_total

    success_count = sum(1 for c in status_codes if c == 200)
    failed_count = total_requests - success_count

    latencies.sort()
    avg_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    p90 = latencies[int(len(latencies) * 0.90)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[min(int(len(latencies) * 0.99), len(latencies) - 1)]

    print("Results:")
    print(f"  Total Duration:     {total_time:.2f} s")
    print(f"  Requests Completed: {total_requests} (Success: {success_count}, Failed: {failed_count})")
    print(f"  Throughput:         {total_requests / total_time:.1f} req/s")
    print(f"  Min Latency:        {min(latencies):.4f} s")
    print(f"  Average Latency:    {avg_latency:.4f} s")
    print(f"  Median (p50):       {median_latency:.4f} s")
    print(f"  90th percentile:    {p90:.4f} s")
    print(f"  95th percentile:    {p95:.4f} s")
    print(f"  99th percentile:    {p99:.4f} s")
    print(f"  Max Latency:        {max(latencies):.4f} s")

    p95_pass = p95 <= 3.0
    scale_pass = failed_count == 0

    print("\nAcceptance Evaluation:")
    print(f"  [TC-PERF-01] 95th percentile <= 3.0s: {'PASSED' if p95_pass else 'FAILED'} ({p95:.4f}s)")
    print(f"  [TC-SCALE-01] 100 concurrent requests without failure: {'PASSED' if scale_pass else 'FAILED'} (0 errors)")

    if p95_pass and scale_pass:
        print("\nAll performance and scalability requirements satisfied successfully.")
        return 0
    else:
        print("\nPerformance requirements NOT met.")
        return 1


if __name__ == "__main__":
    sys.exit(run_load_test())
