
from rest_framework import serializers 
from ..models import Course


class CourseSerializer(serializers.ModelSerializer):
    instructor_display = serializers.CharField(source="instructor.username" , read_only=True)
    level_display = serializers.CharField(source="get_level_display" , read_only=True)
    category_display = serializers.CharField(source="category.name" , read_only=True)
    
    class Meta:
        model = Course
        fields = ["id" ,"title" , "level" ,"level_display" ,  "description" ,  "instructor" ,"instructor_display"  , "category" ,"category_display" ,  "created_at" , "updated_at"]
        read_only_fields= ["created_at" ,"updated_at" , "is_published" , "instructor"]