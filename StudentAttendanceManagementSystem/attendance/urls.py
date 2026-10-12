from django.urls import path
from . import views, attendance_views

urlpatterns = [
    path("faculty/", views.faculty_dashboard, name="faculty_dashboard"),
    path("faculty/mark/<int:course_id>/", attendance_views.mark_attendance, name="mark_attendance"),
    path("faculty/course/<int:course_id>/history/", attendance_views.attendance_history, name="attendance_history"),
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("student/my-attendance/", attendance_views.student_attendance, name="student_attendance"),
]
