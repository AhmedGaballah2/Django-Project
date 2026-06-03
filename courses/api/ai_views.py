from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.ai.agents import handle_chat
from courses.ai.recommender import recommend_courses
from courses.models import Course, CourseDocument, Enrollment

from .permissions import IsEnrolledStudent, IsInstructor
from .serializers import CourseDocumentSerializer, CourseSerializer


class CourseRecommendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.profile.role != "student":
            return Response(
                {"error": "Only students can use the course recommender."},
                status=status.HTTP_403_FORBIDDEN,
            )
        query = request.data.get("query", "").strip()
        if not query:
            return Response(
                {"error": "query is required in the request body."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            results = recommend_courses(query, request.user)
        except RuntimeError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        payload = []
        for item in results:
            course_data = CourseSerializer(item["course"]).data
            payload.append(
                {
                    "course": course_data,
                    "explanation": item["explanation"],
                    "relevance_score": item["relevance_score"],
                }
            )
        return Response(payload, status=status.HTTP_200_OK)


class CourseChatAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEnrolledStudent]

    def post(self, request, id):
        course = get_object_or_404(Course, pk=id)
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"error": "You must be enrolled in this course to use the assistant."},
                status=status.HTTP_403_FORBIDDEN,
            )
        message = request.data.get("message", "").strip()
        if not message:
            return Response(
                {"error": "message is required in the request body."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = handle_chat(request.user, course, message)
        except RuntimeError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(result, status=status.HTTP_200_OK)


class CourseDocumentUploadAPIView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def post(self, request, id):
        course = get_object_or_404(Course, pk=id)
        if course.instructor != request.user:
            return Response(
                {"error": "You can only upload documents for your own courses."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = CourseDocumentSerializer(data=request.data)
        if serializer.is_valid():
            doc = serializer.save(course=course)
            return Response(
                CourseDocumentSerializer(doc).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
