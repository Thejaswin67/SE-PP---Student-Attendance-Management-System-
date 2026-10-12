# Student Attendance Management System (SAMS)

Beginner-friendly Django + MySQL web portal based directly on the academic mini-project documentation. The documentation specifies HTML5/CSS3/JavaScript at the presentation layer, Django at the application layer, and MySQL at the data layer.

## Technology

- Presentation: HTML5, CSS3, JavaScript
- Application: Python Django
- Database: MySQL
- PDF: ReportLab

## Included Modules

- Authentication: login, logout, role-based access, password reset
- Admin: departments, students, faculty, courses, enrollments, dashboard and PDF report
- Faculty: assigned courses, mark Present/Absent/Late, attendance history
- Student: personal attendance, subject filter and low-attendance notification
- Attendance threshold: 75%

## Folder Structure

```text
StudentAttendanceManagementSystem/
├── manage.py
├── requirements.txt
├── database_setup.sql
├── README.md
├── sams/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── attendance/
│   ├── __init__.py
│   ├── admin.py
│   ├── admin_urls.py
│   ├── admin_views.py
│   ├── apps.py
│   ├── attendance_views.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── utils.py
│   ├── views.py
│   ├── migrations/0001_initial.py
│   ├── management/commands/seed_demo.py
│   └── templatetags/sams_tags.py
├── templates/
└── static/
```

## 1. Create the MySQL Database

Open MySQL Workbench and run:

```sql
CREATE DATABASE IF NOT EXISTS sams_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

## 2. Open the project in VS Code

Open this folder:

```text
StudentAttendanceManagementSystem
```

## 3. Create a virtual environment

PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can still use the project by running commands with `venv\Scripts\python.exe`, or open Command Prompt and use:

```cmd
venv\Scripts\activate
```

## 4. Install packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure MySQL password

Open:

```text
sams/settings.py
```

By default it uses:

```text
Database: sams_db
Username: root
Password: blank
Host: 127.0.0.1
Port: 3306
```

If your MySQL root account has a password, set an environment variable before running Django:

```powershell
$env:DB_PASSWORD="YOUR_MYSQL_PASSWORD"
```

Or directly change this line in `settings.py`:

```python
"PASSWORD": os.environ.get("DB_PASSWORD", ""),
```

to:

```python
"PASSWORD": "YOUR_MYSQL_PASSWORD",
```

## 6. Run migrations

```powershell
python manage.py migrate
```

## 7. Create demo users and data

```powershell
python manage.py seed_demo
```

Demo accounts:

```text
ADMIN
Username: admin
Password: admin123

FACULTY
Username: faculty
Password: faculty123

STUDENT
Username: student
Password: student123
```

The demo data includes:

- Information Technology department
- Test Faculty (FAC001)
- Student Thejaswin S (412625205046)
- SE101 Software Engineering
- Student enrollment
- 20 demo attendance records (18 Present + 2 Absent = 90%)

## 8. Start the web portal

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## 9. Test the roles

### Admin

Login as `admin`.

You can manage departments, students, faculty, courses and enrollments, see dashboard statistics, and download the attendance PDF.

### Faculty

Login as `faculty`.

You can see assigned courses, choose a class date, and mark each enrolled student as Present, Absent, or Late.

### Student

Login as `student`.

You can see your own attendance percentage, attendance records and low-attendance notifications.

## Authentication

Authentication uses Django's built-in session authentication. Access to Admin, Faculty and Student pages is controlled by the UserProfile role.

Password reset is included. Because this is a local academic project, the email backend is configured to print reset emails in the Django terminal instead of sending real email.

## Important beginner note

This is intentionally a simple academic web project. There is no React, Node.js, REST API, Docker or separate frontend build process. The goal is that you can understand every file and explain it in a viva.
