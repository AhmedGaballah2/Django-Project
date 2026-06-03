
from django.urls import path


from . import views 


urlpatterns=[
    # path("courses" , views.courses_list , name="courses"),
    path("courses" , views.CoursesAPIView.as_view()),
    # path("courses/<int:id>" , views.single_course , name="single_course"),
    path("courses/<int:id>" , views.CoursesAPIView.as_view() , name="single_course"),

    path("my-enrollments" , views.StudentEnrollmentsAPIView.as_view() , name = "student-enrollment"),

    # path("my-enrollments" , views.student_enrollment , name = "student-enrollment"),
    
    path("courses/<int:id>/enroll" , views.EnrollStudentAPIView.as_view() , name="enroll-course" ),
    path("my-courses" , views.InstructorCoursesAPIView.as_view() ),
    
]