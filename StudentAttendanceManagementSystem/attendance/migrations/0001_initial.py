from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("code", models.CharField(max_length=20, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("ADMIN", "Admin"), ("FACULTY", "Faculty"), ("STUDENT", "Student")], max_length=20)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Faculty",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("employee_id", models.CharField(max_length=30, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="attendance.department")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="faculty_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("register_number", models.CharField(max_length=30, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("year", models.PositiveSmallIntegerField(default=2)),
                ("section", models.CharField(default="A", max_length=10)),
                ("phone", models.CharField(blank=True, max_length=15)),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="attendance.department")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="student_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["register_number"]},
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("course_code", models.CharField(max_length=30, unique=True)),
                ("course_name", models.CharField(max_length=150)),
                ("semester", models.PositiveSmallIntegerField(default=4)),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="attendance.department")),
                ("faculty", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="courses", to="attendance.faculty")),
            ],
            options={"ordering": ["course_code"]},
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="attendance.student")),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="attendance.course")),
            ],
            options={"constraints": [models.UniqueConstraint(fields=("student", "course"), name="unique_student_course")]},
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("status", models.CharField(choices=[("PRESENT", "Present"), ("ABSENT", "Absent"), ("LATE", "Late")], max_length=10)),
                ("marked_at", models.DateTimeField(auto_now=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="attendance.course")),
                ("marked_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="attendance.student")),
            ],
            options={"ordering": ["-date", "student__register_number"], "constraints": [models.UniqueConstraint(fields=("student", "course", "date"), name="unique_attendance_per_day")]},
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_read", models.BooleanField(default=False)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
