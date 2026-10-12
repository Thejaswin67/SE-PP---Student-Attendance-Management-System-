from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import Attendance, Course, Department, Enrollment, Faculty, Student, UserProfile
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Create beginner-friendly demo data for the Student Attendance Management System"

    def handle(self, *args, **options):
        it, _ = Department.objects.get_or_create(code="IT", defaults={"name": "Information Technology"})
        cse, _ = Department.objects.get_or_create(code="CSE", defaults={"name": "Computer Science Engineering"})

        admin, _ = User.objects.get_or_create(username="admin")
        admin.set_password("admin123")
        admin.email = "admin@example.com"
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.save()
        UserProfile.objects.update_or_create(user=admin, defaults={"role": "ADMIN"})

        faculty_user, _ = User.objects.get_or_create(username="faculty")
        faculty_user.set_password("faculty123")
        faculty_user.email = "faculty@example.com"
        faculty_user.first_name = "Test Faculty"
        faculty_user.is_active = True
        faculty_user.save()
        UserProfile.objects.update_or_create(user=faculty_user, defaults={"role": "FACULTY"})
        faculty, _ = Faculty.objects.get_or_create(
            employee_id="FAC001",
            defaults={"user": faculty_user, "name": "Test Faculty", "department": it},
        )
        faculty.user = faculty_user
        faculty.save()

        student_user, _ = User.objects.get_or_create(username="student")
        student_user.set_password("student123")
        student_user.email = "student@example.com"
        student_user.first_name = "Thejaswin S"
        student_user.is_active = True
        student_user.save()
        UserProfile.objects.update_or_create(user=student_user, defaults={"role": "STUDENT"})
        student, _ = Student.objects.get_or_create(
            register_number="412625205046",
            defaults={
                "user": student_user,
                "name": "Thejaswin S",
                "department": it,
                "year": 2,
                "section": "A",
                "phone": "9360682183",
            },
        )
        student.user = student_user
        student.save()

        course, _ = Course.objects.get_or_create(
            course_code="SE101",
            defaults={
                "course_name": "Software Engineering",
                "semester": 4,
                "department": it,
                "faculty": faculty,
            },
        )
        course.faculty = faculty
        course.department = it
        course.save()
        Enrollment.objects.get_or_create(student=student, course=course)

        # Demo attendance: 18 Present + 2 Absent = 90%
        for offset in range(1, 21):
            day = date.today() - timedelta(days=offset)
            status = "ABSENT" if offset in (5, 12) else "PRESENT"
            Attendance.objects.update_or_create(
                student=student,
                course=course,
                date=day,
                defaults={"status": status, "marked_by": faculty_user},
            )

        self.stdout.write(self.style.SUCCESS("Demo data created/updated successfully."))
        self.stdout.write("Admin:   admin / admin123")
        self.stdout.write("Faculty: faculty / faculty123")
        self.stdout.write("Student: student / student123")
