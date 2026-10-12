from django import forms
from django.contrib.auth.models import User
from .models import Course, Department, Enrollment, Faculty, Student


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "code"]


class StudentForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Login Username")
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank while editing.")

    class Meta:
        model = Student
        fields = ["register_number", "name", "department", "year", "section", "phone"]


class FacultyForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Login Username")
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank while editing.")

    class Meta:
        model = Faculty
        fields = ["employee_id", "name", "department"]


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["course_code", "course_name", "semester", "department", "faculty"]


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "course"]
