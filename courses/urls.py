from django.urls import path
from . import views


urlpatterns = [
    path ("" ,  views.courses , name="courses"),
    path ("<slug:slug>" ,  views.course_details , name="course-details")


]