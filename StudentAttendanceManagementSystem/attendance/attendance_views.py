from datetime import date, timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .models import Attendance, Course, Enrollment, Notification
from .utils import attendance_percentage, assigned_course_for_faculty, role_required


@role_required("FACULTY")
def mark_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.faculty != request.user.faculty_profile:
        messages.error(request, "You can only mark attendance for your assigned courses.")
        return redirect("faculty_dashboard")

    enrollments = list(
        Enrollment.objects.filter(course=course)
        .select_related("student")
        .order_by("student__register_number")
    )
    selected_date = request.GET.get("date", str(date.today()))
    try:
        selected_date = date.fromisoformat(selected_date)
    except ValueError:
        selected_date = date.today()

    existing = {
        record.student_id: record
        for record in Attendance.objects.filter(course=course, date=selected_date)
    }

    if request.method == "POST":
        posted_date = request.POST.get("attendance_date", str(selected_date))
        try:
            selected_date = date.fromisoformat(posted_date)
        except ValueError:
            messages.error(request, "Invalid date.")
            return redirect("mark_attendance", course_id=course.id)

        if selected_date > date.today():
            messages.error(request, "Attendance cannot be marked for a future date.")
            return redirect("mark_attendance", course_id=course.id)

        statuses = {}
        for enrollment in enrollments:
            key = f"status_{enrollment.student_id}"
            status = request.POST.get(key)
            if status not in {"PRESENT", "ABSENT", "LATE"}:
                messages.error(request, f"Please select attendance for {enrollment.student.name}.")
                return redirect(f"/attendance/faculty/mark/{course.id}/?date={selected_date.isoformat()}")
            statuses[enrollment.student_id] = status

        # Existing attendance records may only be changed within the configured edit window.
        existing_records = {
            r.student_id: r for r in Attendance.objects.filter(course=course, date=selected_date)
        }
        window = timedelta(hours=settings.ATTENDANCE_EDIT_WINDOW_HOURS)
        now = timezone.now()
        for student_id in statuses:
            old_record = existing_records.get(student_id)
            if old_record is not None and now - old_record.marked_at > window:
                date_text = selected_date.strftime("%d-%m-%Y")
                messages.error(
                    request,
                    f"The attendance for {date_text} is older than the {settings.ATTENDANCE_EDIT_WINDOW_HOURS}-hour edit window."
                )
                return redirect(f"/attendance/faculty/mark/{course.id}/?date={selected_date.isoformat()}")

        with transaction.atomic():
            for student_id, status in statuses.items():
                Attendance.objects.update_or_create(
                    student_id=student_id,
                    course=course,
                    date=selected_date,
                    defaults={"status": status, "marked_by": request.user},
                )

        # Create low-attendance notifications for student, their faculty, and site admins.
        for enrollment in enrollments:
            percentage = attendance_percentage(enrollment.student, course)
            if percentage < settings.ATTENDANCE_THRESHOLD:
                message = f"Low attendance alert for {course.course_code}: {percentage}% attendance."
                if not Notification.objects.filter(user=enrollment.student.user, message=message, is_read=False).exists():
                    Notification.objects.create(user=enrollment.student.user, message=message)
                faculty_message = f"Low attendance: {enrollment.student.name} has {percentage}% in {course.course_code}."
                if not Notification.objects.filter(user=course.faculty.user, message=faculty_message, is_read=False).exists():
                    Notification.objects.create(user=course.faculty.user, message=faculty_message)
                for admin_user in User.objects.filter(userprofile__role="ADMIN", is_active=True):
                    admin_message = f"Low attendance: {enrollment.student.name} has {percentage}% in {course.course_code}."
                    if not Notification.objects.filter(user=admin_user, message=admin_message, is_read=False).exists():
                        Notification.objects.create(user=admin_user, message=admin_message)
        messages.success(request, f"Attendance saved for {course.course_code} on {selected_date.strftime('%d-%m-%Y')}.")
        return redirect("mark_attendance", course_id=course.id)

    return render(
        request,
        "attendance/mark_attendance.html",
        {"course": course, "enrollments": enrollments, "existing": existing, "selected_date": selected_date},
    )


@role_required("FACULTY")
def attendance_history(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.faculty != request.user.faculty_profile:
        messages.error(request, "You cannot access this course.")
        return redirect("faculty_dashboard")
    records = Attendance.objects.filter(course=course).select_related("student").order_by("-date", "student__register_number")
    return render(request, "attendance/attendance_history.html", {"course": course, "records": records})


@role_required("STUDENT")
def student_attendance(request):
    student = request.user.student_profile
    selected_course_id = request.GET.get("course")
    enrollments = Enrollment.objects.filter(student=student).select_related("course")
    records = Attendance.objects.filter(student=student).select_related("course")
    if selected_course_id:
        records = records.filter(course_id=selected_course_id)
    return render(
        request,
        "attendance/student_attendance.html",
        {
            "student": student,
            "enrollments": enrollments,
            "records": records,
            "selected_course_id": selected_course_id,
            "threshold": settings.ATTENDANCE_THRESHOLD,
        },
    )
