from rest_framework.decorators import api_view ,permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.exceptions import NotFound , ValidationError
from rest_framework.response import Response
from ..models import Course , Enrollment
from .serializers import CourseSerializer , StudentEnrollmentSerializer
from django.shortcuts import get_object_or_404
from .permissions import IsInstructorOrReadOnly , IsStudent ,IsInstructor ,IsOwner
from django.db.models import Q
from rest_framework.views import APIView






class   CoursesAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        
      
        return [IsAuthenticated() , IsInstructor() , IsOwner()]
  

    def get_object(self,id):
        try:
         
           course = Course.objects.get(pk=id)
           return course
        except Course.DoesNotExist :
            raise NotFound({"error":"there is no course matches this id"})
        

    def get(self ,request,id=None):
        if id :
            course  = self.get_object(id)
            serializer = CourseSerializer(course)
            return Response(serializer.data,status.HTTP_200_OK)
        courses = Course.objects.filter(is_published=True)
        serializer = CourseSerializer(courses,many=True)
        return Response(serializer.data , status.HTTP_200_OK)
    

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(instructor=request.user)
            return Response(serializer.data , status.HTTP_201_CREATED)
        return Response(serializer.errors , status.HTTP_400_BAD_REQUEST)
    


    def delete(self , request ,id):
        course = self.get_object(id)
        self.check_object_permissions(request,course)
        course.delete()
        return Response(status.HTTP_204_NO_CONTENT)
    


    def put(self,request,id):
        course = self.get_object(id)
        self.check_object_permissions(request,course)

        serializer = CourseSerializer(course,data=request.data , partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status.HTTP_200_OK)
        return Response(serializer.errors , status.HTTP_400_BAD_REQUEST)
            

class StudentEnrollmentsAPIView(APIView):
    permission_classes=[IsAuthenticated ,IsStudent]
    def get(self,request):
        enrollments= Enrollment.objects.filter(student=request.user)
        serializer =   StudentEnrollmentSerializer(enrollments,many=True)
        return Response(serializer.data , status.HTTP_200_OK)



class EnrollStudentAPIView(APIView):
    permission_classes=[IsAuthenticated,IsStudent]


    def post(self,request,id):
        try:
           course = Course.objects.get(pk=id)
           if Enrollment.objects.filter(student = request.user , course=course).exists():
               return Response({"error":"you has been enrolled in this course before"},status.HTTP_400_BAD_REQUEST)
           enrollment = Enrollment.objects.create(student = request.user , course=course)
           serializer =   StudentEnrollmentSerializer(enrollment)
           return Response(serializer.data , status.HTTP_201_CREATED)
        except Course.DoesNotExist:
            return NotFound({"error":"there is no course match this id"}) 
        
        
class InstructorCoursesAPIView(APIView):
    permission_classes=[IsAuthenticated,IsInstructor]
    def get (self , request):
        courses = Course.objects.filter(instructor = request.user)
        serializer = CourseSerializer(courses,many=True)
        return Response(serializer.data , status.HTTP_200_OK)








@api_view(["GET","POST"])
@permission_classes([IsInstructorOrReadOnly])
def courses_list(request):


    if request.method == "POST":
       serializer = CourseSerializer(data=request.data)
       if serializer.is_valid():
           serializer.save(instructor=request.user)
           return Response(serializer.data , status.HTTP_201_CREATED)
       else:
        #    raise ValidationError(serializer.errors)
           return Response(serializer.errors , status.HTTP_400_BAD_REQUEST)
       

    courses = Course.objects.filter(is_published=True,)
    level = request.query_params.get("level")
    if level :
        courses = courses.filter(level=level)

    category = request.query_params.get("category")
    if category:
        print(category)
        courses =courses.filter(category__slug=category)

    search = request.query_params.get("search")
    if search :
        courses = courses.filter(
           Q(title__icontains=search) |
           Q(description__icontains=search)|
           Q(category__name__icontains=search)
        )
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
    try:
        course = Course.objects.get(pk=id)
    except Course.DoesNotExist:
        raise NotFound("there is no course matches this id")
    if Enrollment.objects.filter(course = course , student=request.user).exists:
        raise ValidationError({"detail" :"You are already enrolled in this course."})
    enrollment =  Enrollment.objects.create(student = request.user , course=course)
    serializer = StudentEnrollmentSerializer(enrollment)
    return Response(serializer.data , status.HTTP_201_CREATED)




@api_view(["GET"])
@permission_classes([IsAuthenticated,IsInstructor]) 
def instructor_courses(request):
    courses = Course.objects.filter(instructor=request.user)
    serializer =  CourseSerializer(courses,many=True)
    return Response(serializer.data , status.HTTP_200_OK)














