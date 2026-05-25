from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.


# @login_required
def courses(request):
    return render (request , "courses/courses.html")





# @login_required
def course_details(request , slug ):
    return render (request , "courses/course-details.html")
