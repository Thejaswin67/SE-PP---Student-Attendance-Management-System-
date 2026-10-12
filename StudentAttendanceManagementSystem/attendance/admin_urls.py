from django.urls import path
from . import admin_views

urlpatterns = [
    path("", admin_views.admin_dashboard, name="admin_dashboard"),
    path("departments/", admin_views.department_list, name="department_list"),
    path("departments/add/", admin_views.department_add, name="department_add"),
    path("departments/<int:department_id>/delete/", admin_views.department_delete, name="department_delete"),
    path("students/", admin_views.student_list, name="student_list"),
    path("students/add/", admin_views.student_add, name="student_add"),
    path("students/<int:student_id>/edit/", admin_views.student_edit, name="student_edit"),
    path("students/<int:student_id>/delete/", admin_views.student_delete, name="student_delete"),
    path("faculty/", admin_views.faculty_list, name="faculty_list"),
    path("faculty/add/", admin_views.faculty_add, name="faculty_add"),
    path("faculty/<int:faculty_id>/delete/", admin_views.faculty_delete, name="faculty_delete"),
    path("courses/", admin_views.course_list, name="course_list"),
    path("courses/add/", admin_views.course_add, name="course_add"),
    path("courses/<int:course_id>/delete/", admin_views.course_delete, name="course_delete"),
    path("enrollments/", admin_views.enrollment_list, name="enrollment_list"),
    path("enrollments/add/", admin_views.enrollment_add, name="enrollment_add"),
    path("enrollments/<int:enrollment_id>/delete/", admin_views.enrollment_delete, name="enrollment_delete"),
    path("reports/", admin_views.report_page, name="report_page"),
    path("reports/pdf/", admin_views.report_pdf, name="report_pdf"),
]
