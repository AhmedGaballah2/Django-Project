# Courses Platform

A Django-based learning management system that allows instructors to create and manage courses, and students to enroll in courses. The platform includes both web and REST API interfaces.

## Features

- **User Authentication**: Secure user registration and login system
- **User Roles**: Support for two user types - Instructors and Students
- **Course Management**: Create, edit, delete, and publish courses
- **Course Categories**: Organize courses by categories
- **Course Levels**: Classify courses by difficulty (Beginner, Intermediate, Advanced)
- **Course Enrollment**: Students can enroll in courses
- **Instructor Dashboard**: View and manage courses created by instructors
- **Student Dashboard**: View enrolled courses and course details
- **REST API**: Full REST API for courses management
- **Admin Panel**: Django admin interface for superusers

## Tech Stack

- **Backend**: Django 6.0.5
- **API**: Django REST Framework 3.17.1
- **Database**: SQLite (default, configurable)
- **Frontend**: Django Templates with HTML/CSS
- **Python**: 3.x

## Requirements

- Python 3.8+
- Django 6.0.5
- Django REST Framework 3.17.1
- asgiref 3.11.1
- sqlparse 0.5.5

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd courses_platform
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirments.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create a Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Project Structure

```
courses_platform/
├── accounts/                  # User authentication and profiles
│   ├── api/                  # API views for accounts
│   ├── migrations/           # Database migrations
│   ├── static/               # Static files (CSS, JS, images)
│   ├── templates/            # HTML templates
│   ├── models.py             # User Profile model
│   ├── views.py              # Authentication views
│   ├── forms.py              # Forms
│   └── urls.py               # URL routes
│
├── courses/                   # Course management
│   ├── api/                  # REST API endpoints
│   ├── migrations/           # Database migrations
│   ├── static/               # Static files
│   ├── templates/            # HTML templates
│   ├── models.py             # Course, Category, Enrollment models
│   ├── views.py              # Course views
│   ├── forms.py              # Course forms
│   ├── decorators.py         # Custom decorators
│   └── urls.py               # URL routes
│
├── courses_platform/          # Project settings
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL configuration
│   ├── wsgi.py               # WSGI application
│   └── asgi.py               # ASGI application
│
├── templates/                 # Base templates
│   ├── base.html             # Base template
│   └── nav.html              # Navigation template
│
├── manage.py                  # Django CLI
├── db.sqlite3                 # SQLite database
└── requirments.txt            # Python dependencies
```

## Database Models

### Accounts App

**Profile**
- `owner` (OneToOne): Link to Django User
- `role` (Choice): "instructor" or "student"
- `bio` (CharField): User biography (optional)

### Courses App

**Category**
- `name` (CharField): Category name
- `slug` (SlugField): URL-friendly name (unique)

**Course**
- `title` (CharField): Course title
- `description` (TextField): Course description
- `instructor` (ForeignKey): Link to User
- `category` (ForeignKey): Link to Category
- `level` (Choice): "beginner", "intermediate", or "advanced"
- `is_published` (BooleanField): Publication status
- `created_at` (DateTimeField): Creation timestamp
- `updated_at` (DateTimeField): Last update timestamp

**Enrollment**
- `student` (ForeignKey): Link to User
- `course` (ForeignKey): Link to Course
- `enrolled_at` (DateTimeField): Enrollment timestamp
- **Constraint**: A student can only enroll once per course

## URL Routes

### Accounts
- `/accounts/register/` - User registration
- `/accounts/login/` - User login
- `/accounts/profile/` - User profile setup

### Courses
- `/courses/` - View all courses
- `/courses/<id>/` - View course details
- `/courses/create/` - Create a new course (Instructor only)
- `/courses/<id>/edit/` - Edit course (Instructor only)
- `/courses/<id>/delete/` - Delete course (Instructor only)
- `/courses/instructor/` - Instructor's course dashboard
- `/courses/enroll/<course_id>/` - Enroll in a course (Student only)
- `/courses/student/` - Student's enrollment dashboard

### API (REST)
- `/api/v1/` - API root
- `/api/v1/courses/` - List/Create courses
- `/api/v1/courses/<id>/` - Retrieve/Update course

## User Workflow

### For Students
1. Register for an account
2. Set up profile and select "Student" role
3. View available courses
4. Enroll in courses
5. View enrolled courses in dashboard

### For Instructors
1. Register for an account
2. Set up profile and select "Instructor" role
3. Create new courses with categories and levels
4. Manage course content (edit/delete)
5. Publish courses for students
6. View enrolled students

## Development Notes

- The project uses Django's authentication system
- REST API uses Token Authentication via Django REST Framework
- Static files are served via `django.contrib.staticfiles`
- Admin panel is available at `/admin/`
- Templates are rendered using Django Template Language (DTL)

## Admin Panel

Access admin panel at `/admin/` with your superuser credentials. Manage:
- Users
- User Profiles
- Courses
- Categories
- Enrollments

## Common Commands

```bash
# Create migrations for changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Collect static files (for production)
python manage.py collectstatic

# Run tests
python manage.py test

# Interactive Python shell with Django context
python manage.py shell
```

## Environment Configuration

### Settings to Customize for Production
In `courses_platform/settings.py`:
- `SECRET_KEY`: Change to a secure random key
- `DEBUG`: Set to `False`
- `ALLOWED_HOSTS`: Add your domain names
- `DATABASES`: Configure your production database
- Add SSL/HTTPS configuration
- Configure CORS if needed for API

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, please refer to Django documentation:
- [Django Official Docs](https://docs.djangoproject.com/)
- [Django REST Framework Docs](https://www.django-rest-framework.org/)