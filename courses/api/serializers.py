
from rest_framework import serializers 
from ..models import Course , Enrollment, CourseDocument


class CourseSerializer(serializers.ModelSerializer):
    instructor_display = serializers.CharField(source="instructor.username" , read_only=True)
    level_display = serializers.CharField(source="get_level_display" , read_only=True)
    category_display = serializers.CharField(source="category.name" , read_only=True)
    
    class Meta:
        model = Course
        fields = ["id" ,"title" , "level" ,"level_display" ,  "description" ,  "instructor" ,"instructor_display"  , "category" ,"category_display" ,  "created_at" , "updated_at", "is_published"]
        read_only_fields= ["created_at" ,"updated_at" , "is_published" , "instructor"]







class StudentEnrollmentSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="course.title" , read_only=True)
    category = serializers.CharField(source="course.category.name" , read_only=True )
    level = serializers.CharField(source ="course.level" ,  read_only=True)
    instructor = serializers.CharField(source="course.instructor" , read_only=True)
    class Meta:
        model = Enrollment
        fields = [ "student" , "course", "enrolled_at" ,   "title"   , "instructor" , "level" , "category" ]


class CourseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDocument
        fields = ["id", "course", "title", "file", "uploaded_at"]
        read_only_fields = ["course", "uploaded_at"]
