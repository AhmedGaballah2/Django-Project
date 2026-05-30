
from django.urls import path


from . import views 


urlpatterns=[
    path("courses" , views.courses_list , name="courses"),
    path("courses/<int:id>" , views.single_course , name="single_course")
]