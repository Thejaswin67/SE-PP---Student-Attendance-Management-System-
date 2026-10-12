from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings
from django.db.models import Q
from .models import Attendance, Enrollment, Notification, Student, UserProfile


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            try:
                role = request.user.userprofile.role
            except UserProfile.DoesNotExist:
                messages.error(request, "Your account does not have a role assigned.")
                return redirect("login")
            if role not in allowed_roles:
                messages.error(request, "You do not have permission to access that page.")
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def attendance_percentage(student, course=None):
    qs = Attendance.objects.filter(student=student)
    if course is not None:
        qs = qs.filter(course=course)
    total = qs.count()
    if total == 0:
        return 0.0
    present = qs.filter(Q(status="PRESENT") | Q(status="LATE")).count() if settings.LATE_COUNTS_AS_PRESENT else qs.filter(status="PRESENT").count()
    return round((present / total) * 100, 2)


def create_low_attendance_notifications():
    students = Student.objects.select_related("user").all()
    for student in students:
        percentage = attendance_percentage(student)
        if percentage < settings.ATTENDANCE_THRESHOLD and Attendance.objects.filter(student=student).exists():
            message = f"Low attendance alert: your current attendance is {percentage}% (below {settings.ATTENDANCE_THRESHOLD}%)."
            exists = Notification.objects.filter(user=student.user, message=message, is_read=False).exists()
            if not exists:
                Notification.objects.create(user=student.user, message=message)


def assigned_course_for_faculty(user, course_id):
    return user.faculty_profile.courses.filter(id=course_id).first()
