from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug  = models.SlugField(unique=True)



    def __str__(self):
        return f"{self.name}"
    


class Course(models.Model):

    LEVEL_CHOICES = [
        ("beginner" , "Beginner"),
        ("intermediate" , "Intermediate"),
        ("advanced" , "Advanced")
    ]



    title = models.CharField(max_length=200)
    description= models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE , related_name="courses")
    category = models.ForeignKey(Category, on_delete=models.CASCADE , related_name="courses")
    level = models.CharField( max_length=50 , choices=LEVEL_CHOICES)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return f"{self.title}"




class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE , related_name="enrollments")
    course = models.ForeignKey(Course,  on_delete=models.CASCADE ,related_name="enrollments")
    enrolled_at = models.DateTimeField( auto_now_add=True)


    class Meta:
        unique_together= ('student', 'course')


class CourseDocument(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="course_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]
    SOURCE_CHOICES = [
        ("RAG", "RAG"),
        ("General", "General"),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_messages")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chat_messages")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.student.username} — {self.course.title} ({self.role})"


class RecommendChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recommend_chat_messages"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    recommendations_data = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.student.username} — recommend ({self.role})"