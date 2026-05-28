from django.urls import path
from . import views


urlpatterns = [
    path ("" ,  views.courses , name="courses"),
    path("instructor-courses" , views.instructor_courses , name="instructor-courses"),
    path("create" , views.create_course , name="create-course"),
    path("<int:id>/delete" , views.delete_course , name="delete-course"),
    path("<int:id>/edit" , views.edit_course , name="edit-course"),
    path("<int:id>/enroll", views.enroll_course, name= "enroll-course") ,
    path("my-enrollments" , views.student_enrollments , name="student-enrollments"),

    path ("<int:id>" ,  views.course_details , name="course-details"),


]