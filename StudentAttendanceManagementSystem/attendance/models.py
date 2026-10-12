from django.contrib.auth.models import User
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("FACULTY", "Faculty"),
        ("STUDENT", "Student"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Student(models.Model):
    register_number = models.CharField(max_length=30, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    name = models.CharField(max_length=120)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    year = models.PositiveSmallIntegerField(default=2)
    section = models.CharField(max_length=10, default="A")
    phone = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ["register_number"]

    def __str__(self):
        return f"{self.register_number} - {self.name}"


class Faculty(models.Model):
    employee_id = models.CharField(max_length=30, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="faculty_profile")
    name = models.CharField(max_length=120)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.employee_id} - {self.name}"


class Course(models.Model):
    course_code = models.CharField(max_length=30, unique=True)
    course_name = models.CharField(max_length=150)
    semester = models.PositiveSmallIntegerField(default=4)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name="courses")

    class Meta:
        ordering = ["course_code"]

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course")
        ]

    def __str__(self):
        return f"{self.student.register_number} - {self.course.course_code}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("LATE", "Late"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(User, on_delete=models.PROTECT)
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "student__register_number"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course", "date"], name="unique_attendance_per_day")
        ]

    def __str__(self):
        return f"{self.student.register_number} - {self.course.course_code} - {self.date}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.message
