from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from administration.models import Faculty, Student, Subject, Enrolment
from attendance.models import AttendanceSession, Attendance, AuditLog
from attendance.services import log_audit_event

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds sample data for Sprint 2 demo video and testing"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Sprint 2 demo data...")

        # 1. Admin
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={"role": User.Role.ADMIN, "is_staff": True, "is_superuser": True},
        )
        admin_user.set_password("admin123")
        admin_user.role = User.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        # 2. Faculty
        faculty_user, _ = User.objects.get_or_create(
            username="prof_smith",
            defaults={
                "first_name": "Alan",
                "last_name": "Smith",
                "role": User.Role.FACULTY,
            },
        )
        faculty_user.set_password("faculty123")
        faculty_user.save()

        faculty, _ = Faculty.objects.get_or_create(
            faculty_id="FAC101",
            defaults={"user": faculty_user, "department": "Computer Science"},
        )

        # 3. Subjects
        sub1, _ = Subject.objects.get_or_create(
            subject_code="CS201",
            defaults={"subject_name": "Data Structures & Algorithms", "faculty": faculty},
        )
        sub2, _ = Subject.objects.get_or_create(
            subject_code="CS301",
            defaults={"subject_name": "Operating Systems", "faculty": faculty},
        )

        # 4. Students
        # Alice (Normal: 80%+)
        alice_u, _ = User.objects.get_or_create(
            username="alice",
            defaults={"first_name": "Alice", "last_name": "Johnson", "role": User.Role.STUDENT},
        )
        alice_u.set_password("student123")
        alice_u.save()
        alice, _ = Student.objects.get_or_create(
            student_id="STU101",
            defaults={"user": alice_u, "department": "Computer Science", "year_of_study": 2},
        )

        # Bob (Low Attendance Defaulter: 50% < 75%)
        bob_u, _ = User.objects.get_or_create(
            username="bob",
            defaults={"first_name": "Bob", "last_name": "Williams", "role": User.Role.STUDENT},
        )
        bob_u.set_password("student123")
        bob_u.save()
        bob, _ = Student.objects.get_or_create(
            student_id="STU102",
            defaults={"user": bob_u, "department": "Computer Science", "year_of_study": 2},
        )

        # Charlie (Normal: 100%)
        charlie_u, _ = User.objects.get_or_create(
            username="charlie",
            defaults={"first_name": "Charlie", "last_name": "Brown", "role": User.Role.STUDENT},
        )
        charlie_u.set_password("student123")
        charlie_u.save()
        charlie, _ = Student.objects.get_or_create(
            student_id="STU103",
            defaults={"user": charlie_u, "department": "Computer Science", "year_of_study": 2},
        )

        # Enrolments
        for s in [alice, bob, charlie]:
            Enrolment.objects.get_or_create(student=s, subject=sub1)
            Enrolment.objects.get_or_create(student=s, subject=sub2)

        # 5. Sessions & Attendance
        base_date = date.today() - timedelta(days=10)
        dates = [base_date + timedelta(days=i * 2) for i in range(4)]

        # Session 1: Alice Present, Bob Present, Charlie Present
        s1, _ = AttendanceSession.objects.get_or_create(
            subject=sub1,
            session_date=dates[0],
            defaults={"created_by": faculty_user},
        )
        Attendance.objects.update_or_create(session=s1, student=alice, defaults={"status": Attendance.Status.PRESENT, "marked_by": faculty_user})
        Attendance.objects.update_or_create(session=s1, student=bob, defaults={"status": Attendance.Status.PRESENT, "marked_by": faculty_user})
        Attendance.objects.update_or_create(session=s1, student=charlie, defaults={"status": Attendance.Status.PRESENT, "marked_by": faculty_user})

        # Session 2: Alice Present, Bob Absent, Charlie Present
        s2, _ = AttendanceSession.objects.get_or_create(
            subject=sub1,
            session_date=dates[1],
            defaults={"created_by": faculty_user},
        )
        Attendance.objects.update_or_create(session=s2, student=alice, defaults={"status": Attendance.Status.PRESENT, "marked_by": faculty_user})
        Attendance.objects.update_or_create(session=s2, student=bob, defaults={"status": Attendance.Status.ABSENT, "marked_by": faculty_user})
        Attendance.objects.update_or_create(session=s2, student=charlie, defaults={"status": Attendance.Status.PRESENT, "marked_by": faculty_user})

        # Session 3: Alice Late, Bob Absent, Charlie Present
        s3, _ = AttendanceSession.objects.get_or_create(
            subject=sub1,
            session_date=dates[2],
            defaults={"created_by": faculty_user},
        )
        Attendance.objects.update_or_create(session=s3, student=alice, defaults={"status": Attendance.Status.LATE, "marked_by": faculty_user})
        Attendance.objects.update_or_create(session=s3, student=bob, defaults={"status": Attendance.Status.ABSENT, "marked_by": faculty_user})
        Attendance.objects.update_or_create(session=s3, student=charlie, defaults={"status": Attendance.Status.PRESENT, "marked_by": faculty_user})

        # Session 4 (Today): Alice Present, Bob Present (Modified from Absent), Charlie Present
        s4, _ = AttendanceSession.objects.get_or_create(
            subject=sub1,
            session_date=dates[3],
            defaults={"created_by": faculty_user},
        )
        Attendance.objects.update_or_create(session=s4, student=alice, defaults={"status": Attendance.Status.PRESENT, "marked_by": faculty_user})
        rec_bob, _ = Attendance.objects.update_or_create(session=s4, student=bob, defaults={"status": Attendance.Status.PRESENT, "marked_by": faculty_user})
        Attendance.objects.update_or_create(session=s4, student=charlie, defaults={"status": Attendance.Status.PRESENT, "marked_by": faculty_user})

        # Pre-seed audit log entry
        log_audit_event(
            user=faculty_user,
            action="ATTENDANCE_MODIFIED",
            entity="Attendance",
            entity_id=rec_bob.id,
            old_value="ABSENT",
            new_value="PRESENT",
            reason="Student presented medical slip from health center",
        )

        self.stdout.write(self.style.SUCCESS("✓ Sprint 2 demo data seeded successfully!"))
        self.stdout.write("Credentials:")
        self.stdout.write("  Admin:    admin / admin123")
        self.stdout.write("  Faculty:  prof_smith / faculty123")
        self.stdout.write("  Student (Defaulter - 50%): bob / student123")
        self.stdout.write("  Student (Normal - 100%):   charlie / student123")
