from rest_framework.decorators import api_view ,permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.response import Response
from ..models import Course , Enrollment
from .serializers import CourseSerializer , StudentEnrollmentSerializer
from django.shortcuts import get_object_or_404
from .permissions import IsInstructorOrReadOnly , IsStudent





@api_view(["GET","POST"])
@permission_classes([IsInstructorOrReadOnly])
def courses_list(request):


    if request.method == "POST":
       serializer = CourseSerializer(data=request.data)
       if serializer.is_valid():
           serializer.save(instructor=request.user)
           return Response(serializer.data , status.HTTP_201_CREATED)
       else:
           return Response(serializer.errors , status.HTTP_400_BAD_REQUEST)

    courses = Course.objects.filter(is_published=True)
    serializer = CourseSerializer(courses , many=True)
    return Response(serializer.data , status.HTTP_200_OK)






@api_view(["GET","PUT","PATCH","DELETE"])
@permission_classes([IsInstructorOrReadOnly])
def single_course(request , id):


    course = get_object_or_404(Course,pk=id)

    isInstructor = IsInstructorOrReadOnly()

    if not isInstructor.has_object_permission(request , None , course):
        return Response ({"error":"permission denied"} , status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        
        serializer = CourseSerializer(course)
        return Response(serializer.data , status.HTTP_200_OK)
    elif request.method == "DELETE":
        course.delete()
        return Response(status.HTTP_204_NO_CONTENT)
    elif request.method == "PUT":
        serializer = CourseSerializer(course , request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return  Response(serializer.data) 
        
        return Response(serializer.errors , status.HTTP_400_BAD_REQUEST)




@api_view(["GET"])
@permission_classes([IsAuthenticated,IsStudent])
def student_enrollment(request):
      if request.method == "GET":
        enrollments = Enrollment.objects.filter(student=request.user)
        serializer = StudentEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data,status.HTTP_200_OK)
      



@api_view(["POST"])
@permission_classes([IsAuthenticated,IsStudent])
def enroll_course(request , id):
    course = get_object_or_404(Course , pk=id)
    enrollment =  Enrollment.objects.create(student = request.user , course=course)
    serializer = StudentEnrollmentSerializer(enrollment)
    return Response(serializer.data , status.HTTP_201_CREATED)













