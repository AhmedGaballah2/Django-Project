
from django.urls import path

from . import views
from .ai_views import CourseChatAPIView, CourseDocumentUploadAPIView, CourseRecommendAPIView


urlpatterns = [
    path("courses", views.CoursesAPIView.as_view()),
    path("courses/recommend", CourseRecommendAPIView.as_view(), name="api-course-recommend"),
    path("courses/<int:id>", views.CoursesAPIView.as_view(), name="single_course"),
    path("courses/<int:id>/enroll", views.EnrollStudentAPIView.as_view()),
    path("courses/<int:id>/chat", CourseChatAPIView.as_view(), name="course-chat"),
    path("courses/<int:id>/documents", CourseDocumentUploadAPIView.as_view(), name="course-documents"),
    path("my-enrollments", views.StudentEnrollmentsAPIView.as_view(), name="student-enrollment"),
    path("my-courses", views.InstructorCoursesAPIView.as_view()),
]