from django.contrib import admin
from .models import Attendance, Course, Department, Enrollment, Faculty, Notification, Student, UserProfile

admin.site.register(Department)
admin.site.register(UserProfile)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Attendance)
admin.site.register(Notification)
