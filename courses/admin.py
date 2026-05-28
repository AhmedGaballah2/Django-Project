from django.contrib import admin
from .models import Category,Course,Enrollment

# Register your models here.



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields={
        "slug":("name",)
    }
    list_display=["id" ,"name" , "slug"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display=["instructor", "category" ,"level" ,"is_published" ,"created_at" ,"updated_at"]
    


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display=["student","course","enrolled_at"]