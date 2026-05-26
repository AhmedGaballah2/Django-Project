from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import instructors_only
# Create your views here.


@login_required
def courses(request):
    return render (request , "courses/courses.html")





@login_required
def course_details(request , slug ):
    return render (request , "courses/course-details.html")


@login_required
@instructors_only
def instructor_courses(request):
    return render (request , "courses/instructor-courses.html")


