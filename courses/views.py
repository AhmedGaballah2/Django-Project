from django.shortcuts import render ,redirect ,get_object_or_404 
from django.contrib.auth.decorators import login_required
from .decorators import instructors_only ,students_only
from .forms  import CourseForm
from .models import Course ,Enrollment
from django.contrib import messages
from django.db import IntegrityError
from django.core.exceptions import PermissionDenied

# Create your views here.


def courses(request):
    courses = Course.objects.filter(is_published=True)
    return render (request , "courses/courses.html" , {"courses" :courses })





# def course_details(request , id ):
#     course = get_object_or_404(Course,pk=id)
#     is_enrolled = Enrollment.objects.filter(course=course , student=request.user).exists()
#     return render (request , "courses/course-details.html" , {"course":course , "is_enrolled":is_enrolled})

# def course_details(request , id ):
#     course = get_object_or_404(Course,pk=id)
#     is_enrolled = False
#     if request.user.is_authenticated and request.user.profile.role == "student":
#         is_enrolled = Enrollment.objects.filter(course=course , student=request.user).exists()
#     return render (request , "courses/course-details.html" , {"course":course , "is_enrolled":is_enrolled})

def course_details(request , id ):
    course = get_object_or_404(Course,pk=id)
    is_enrolled = Enrollment.objects.filter(course=course , student=request.user).exists()
    return render (request , "courses/course-details.html" , {"course":course , "is_enrolled":is_enrolled})


@login_required
@instructors_only
def instructor_courses(request):
    courses = Course.objects.filter(instructor=request.user)
    return render (request , "courses/instructor-courses.html" , {"courses":courses})


@login_required
@instructors_only
def create_course(request):
     form = CourseForm(request.POST or None)
     if form.is_valid():
         
        course =  form.save(commit=False)
        course.instructor = request.user
        course.save()
        messages.success(request , "Course created successfully")

        return redirect("instructor-courses")
         
     
     return render (request , "courses/create-course.html" , {"form":form}) 





@login_required
@instructors_only
def delete_course(request , id):
    course = get_object_or_404(Course,pk=id , instructor = request.user)

    if request.method == "POST":
          course.delete()
          messages.success(request , "Course Deleted Successfully")
          return redirect ("instructor-courses")
    return render(request , "courses/delete-confirmation.html" , {"title":course.title})



@login_required
@instructors_only
def edit_course(request,id):
     course = get_object_or_404(Course,pk=id, instructor = request.user)
         
     form = CourseForm(request.POST or None , instance=course)
     if form.is_valid():
         form.save()
         messages.success(request , "Course edited Successfully")
         
         return redirect("instructor-courses")
     return render (request , "courses/edit-course.html" , {"form" : form })



@login_required
@students_only
def enroll_course(request , id):
    course = get_object_or_404(Course, pk=id)
    try:
        Enrollment.objects.create(course=course,student=request.user)
        messages.success(request , "You  enrolled Successfully")

    except  IntegrityError :
        messages.error(request , "You has been enrolled this course before")
    finally:
          return redirect("student-enrollments")



@login_required
@students_only
def student_enrollments(request):
    enrollments = Enrollment.objects.filter(student = request.user)
    return render(request , "courses/student-enrollments.html" , {"enrollments":enrollments})
         




