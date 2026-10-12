from io import BytesIO
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from .forms import CourseForm, DepartmentForm, EnrollmentForm, FacultyForm, StudentForm
from .models import Attendance, Course, Department, Enrollment, Faculty, Student, UserProfile
from .utils import attendance_percentage, role_required


@role_required("ADMIN")
def admin_dashboard(request):
    students = Student.objects.count()
    faculty = Faculty.objects.count()
    courses = Course.objects.count()
    attendance = Attendance.objects.count()
    present = Attendance.objects.filter(status__in=["PRESENT", "LATE"]).count()
    attendance_rate = round((present / attendance) * 100, 2) if attendance else 0
    department_data = []
    for department in Department.objects.all():
        department_data.append({
            "name": department.code,
            "students": department.student_set.count(),
        })
    return render(request, "dashboard/admin_dashboard.html", {
        "students": students,
        "faculty": faculty,
        "courses": courses,
        "attendance": attendance,
        "attendance_rate": attendance_rate,
        "department_data": department_data,
        "threshold": settings.ATTENDANCE_THRESHOLD,
    })


@role_required("ADMIN")
def department_list(request):
    return render(request, "admin_panel/department_list.html", {"departments": Department.objects.all()})


@role_required("ADMIN")
def department_add(request):
    form = DepartmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Department added successfully.")
        return redirect("department_list")
    return render(request, "admin_panel/simple_form.html", {"form": form, "title": "Add Department", "cancel_url": "department_list"})


@role_required("ADMIN")
def department_delete(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == "POST":
        department.delete()
        messages.success(request, "Department deleted.")
    return redirect("department_list")


@role_required("ADMIN")
def student_list(request):
    students = Student.objects.select_related("department", "user").all()
    return render(request, "admin_panel/student_list.html", {"students": students})


def _create_user(username, password, role, first_name=""):
    user = User.objects.create_user(username=username, password=password, first_name=first_name, email=f"{username}@example.com")
    UserProfile.objects.create(user=user, role=role)
    return user


@role_required("ADMIN")
def student_add(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"] or "student123"
        if User.objects.filter(username=username).exists():
            form.add_error("username", "This username already exists.")
        else:
            with transaction.atomic():
                user = _create_user(username, password, "STUDENT", form.cleaned_data["name"])
                student = form.save(commit=False)
                student.user = user
                student.save()
            messages.success(request, "Student and login account created successfully.")
            return redirect("student_list")
    return render(request, "admin_panel/simple_form.html", {"form": form, "title": "Add Student", "cancel_url": "student_list"})


@role_required("ADMIN")
def student_edit(request, student_id):
    student = get_object_or_404(Student.objects.select_related("user"), id=student_id)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            username = form.cleaned_data["username"]
            if User.objects.exclude(id=student.user_id).filter(username=username).exists():
                form.add_error("username", "This username already exists.")
            else:
                student.user.username = username
                if form.cleaned_data["password"]:
                    student.user.set_password(form.cleaned_data["password"])
                student.user.save()
                form.save()
                messages.success(request, "Student updated successfully.")
                return redirect("student_list")
    else:
        form = StudentForm(instance=student, initial={"username": student.user.username})
    return render(request, "admin_panel/simple_form.html", {"form": form, "title": "Edit Student", "cancel_url": "student_list"})


@role_required("ADMIN")
def student_delete(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        student.user.delete()
        messages.success(request, "Student and login account deleted.")
    return redirect("student_list")


@role_required("ADMIN")
def faculty_list(request):
    return render(request, "admin_panel/faculty_list.html", {"faculty": Faculty.objects.select_related("department", "user").all()})


@role_required("ADMIN")
def faculty_add(request):
    form = FacultyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"] or "faculty123"
        if User.objects.filter(username=username).exists():
            form.add_error("username", "This username already exists.")
        else:
            with transaction.atomic():
                user = _create_user(username, password, "FACULTY", form.cleaned_data["name"])
                faculty = form.save(commit=False)
                faculty.user = user
                faculty.save()
            messages.success(request, "Faculty and login account created successfully.")
            return redirect("faculty_list")
    return render(request, "admin_panel/simple_form.html", {"form": form, "title": "Add Faculty", "cancel_url": "faculty_list"})


@role_required("ADMIN")
def faculty_delete(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if request.method == "POST":
        faculty.user.delete()
        messages.success(request, "Faculty and login account deleted.")
    return redirect("faculty_list")


@role_required("ADMIN")
def course_list(request):
    courses = Course.objects.select_related("department", "faculty").all()
    return render(request, "admin_panel/course_list.html", {"courses": courses})


@role_required("ADMIN")
def course_add(request):
    form = CourseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course added successfully.")
        return redirect("course_list")
    return render(request, "admin_panel/simple_form.html", {"form": form, "title": "Add Course", "cancel_url": "course_list"})


@role_required("ADMIN")
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted.")
    return redirect("course_list")


@role_required("ADMIN")
def enrollment_list(request):
    enrollments = Enrollment.objects.select_related("student", "course").all()
    return render(request, "admin_panel/enrollment_list.html", {"enrollments": enrollments})


@role_required("ADMIN")
def enrollment_add(request):
    form = EnrollmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student enrolled successfully.")
        return redirect("enrollment_list")
    return render(request, "admin_panel/simple_form.html", {"form": form, "title": "Enroll Student", "cancel_url": "enrollment_list"})


@role_required("ADMIN")
def enrollment_delete(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    if request.method == "POST":
        enrollment.delete()
        messages.success(request, "Enrollment removed.")
    return redirect("enrollment_list")


@role_required("ADMIN")
def _filtered_report_records(request):
    records = Attendance.objects.select_related("student", "course").all()
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    course_id = request.GET.get("course")
    student_id = request.GET.get("student")
    if start_date:
        records = records.filter(date__gte=start_date)
    if end_date:
        records = records.filter(date__lte=end_date)
    if course_id:
        records = records.filter(course_id=course_id)
    if student_id:
        records = records.filter(student_id=student_id)
    return records.order_by("-date", "student__register_number")


@role_required("ADMIN")
def report_page(request):
    records = _filtered_report_records(request)[:300]
    return render(request, "reports/report_page.html", {
        "records": records,
        "threshold": settings.ATTENDANCE_THRESHOLD,
        "courses": Course.objects.order_by("course_code"),
        "students": Student.objects.order_by("register_number"),
        "selected_course": request.GET.get("course", ""),
        "selected_student": request.GET.get("student", ""),
        "start_date": request.GET.get("start_date", ""),
        "end_date": request.GET.get("end_date", ""),
    })


@role_required("ADMIN")
def report_pdf(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    story = [Paragraph("Student Attendance Report", styles["Title"]), Spacer(1, 12)]

    rows = [["Date", "Register No.", "Student", "Course", "Status"]]
    for record in _filtered_report_records(request):
        rows.append([
            record.date.strftime("%d-%m-%Y"),
            record.student.register_number,
            record.student.name,
            record.course.course_code,
            record.status,
        ])

    table = Table(rows, repeatRows=1, colWidths=[80, 110, 180, 110, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="student_attendance_report.pdf"'
    return response
