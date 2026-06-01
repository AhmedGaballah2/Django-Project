
from django.urls import path


from . import views 


urlpatterns=[
    # path("courses" , views.courses_list , name="courses"),
    path("courses" , views.CoursesAPIView.as_view() , name="courses"),
    # path("courses/<int:id>" , views.single_course , name="single_course"),
    path("courses/<int:id>" , views.CoursesAPIView.as_view() , name="single_course"),


    path("my-enrollments" , views.student_enrollment , name = "student-enrollment"),
    path("courses/<int:id>/enroll" , views.enroll_course , name="enroll-course" ),
    path("my-courses" , views.instructor_courses , name = "instructor-courses"),
    
]