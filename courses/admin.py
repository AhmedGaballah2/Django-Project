from django.contrib import admin
from .models import (
    Category,
    Course,
    Enrollment,
    CourseDocument,
    ChatMessage,
    RecommendChatMessage,
)

# Register your models here.



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields={
        "slug":("name",)
    }
    list_display=["id" ,"name" , "slug"]


@admin.action(description="Approve and publish selected courses")
def approve_courses(modeladmin, request, queryset):
    for course in queryset:
        course.is_published = True
        course.save()


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "instructor", "category", "level", "is_published", "created_at"]
    list_filter = ["is_published", "level", "category"]
    search_fields = ["title", "description", "instructor__username"]
    actions = [approve_courses]
    


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display=["student","course","enrolled_at"]


@admin.register(CourseDocument)
class CourseDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "uploaded_at"]
    list_filter = ["course"]
    search_fields = ["title", "course__title"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "role", "source", "created_at"]
    list_filter = ["role", "source", "course"]
    search_fields = ["content", "student__username", "course__title"]


@admin.register(RecommendChatMessage)
class RecommendChatMessageAdmin(admin.ModelAdmin):
    list_display = ["student", "role", "created_at"]
    list_filter = ["role"]
    search_fields = ["content", "student__username"]