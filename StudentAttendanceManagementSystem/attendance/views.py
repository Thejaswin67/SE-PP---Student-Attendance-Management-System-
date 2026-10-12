from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Attendance, Course, Enrollment, Notification
from .forms import LoginForm
from .utils import attendance_percentage, role_required


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user is not None:
            if not user.is_active:
                messages.error(request, "This account is inactive.")
                return render(request, "accounts/login.html", {"form": form})
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


@login_required
def dashboard(request):
    try:
        role = request.user.userprofile.role
    except Exception:
        messages.error(request, "This user has no configured role.")
        return redirect("login")

    if role == "ADMIN":
        return redirect("admin_dashboard")
    if role == "FACULTY":
        return redirect("faculty_dashboard")
    return redirect("student_dashboard")


@role_required("FACULTY")
def faculty_dashboard(request):
    courses = request.user.faculty_profile.courses.all()
    course_data = []
    for course in courses:
        total = Attendance.objects.filter(course=course).count()
        present = Attendance.objects.filter(course=course, status__in=["PRESENT", "LATE"]).count()
        percentage = round((present / total) * 100, 2) if total else 0
        course_data.append({"course": course, "attendance_percentage": percentage, "sessions_marked": total})
    return render(request, "dashboard/faculty_dashboard.html", {"course_data": course_data})


@role_required("STUDENT")
def student_dashboard(request):
    student = request.user.student_profile
    enrollments = Enrollment.objects.filter(student=student).select_related("course")
    course_data = []
    for enrollment in enrollments:
        course_data.append({
            "course": enrollment.course,
            "percentage": attendance_percentage(student, enrollment.course),
        })
    notifications = Notification.objects.filter(user=request.user)[:5]
    return render(
        request,
        "dashboard/student_dashboard.html",
        {"student": student, "course_data": course_data, "notifications": notifications},
    )
