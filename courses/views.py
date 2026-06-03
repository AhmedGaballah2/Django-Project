from django.shortcuts import render ,redirect ,get_object_or_404 
from django.contrib.auth.decorators import login_required
from .decorators import instructors_only ,students_only
from .forms  import CourseForm
from .models import (
    Course,
    Enrollment,
    CourseDocument,
    ChatMessage,
    Category,
    RecommendChatMessage,
)
from .querysets import filter_published_courses
from .forms import CourseDocumentForm
from .ai.agents import handle_chat
from .ai.recommend_chat import handle_recommend_chat
from .ai.config import ai_configured
from django.contrib import messages
from django.db import IntegrityError
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# Create your views here.


def courses(request):
    course_list = Course.objects.filter(is_published=True).select_related(
        "category", "instructor"
    )
    course_list = filter_published_courses(
        course_list,
        search=request.GET.get("search"),
        category=request.GET.get("category"),
        level=request.GET.get("level"),
    )
    categories = Category.objects.all()
    return render(
        request,
        "courses/courses.html",
        {
            "courses": course_list,
            "categories": categories,
            "search": request.GET.get("search", ""),
            "selected_category": request.GET.get("category", ""),
            "selected_level": request.GET.get("level", ""),
        },
    )





# def course_details(request , id ):
#     course = get_object_or_404(Course,pk=id)
#     is_enrolled = Enrollment.objects.filter(course=course , student=request.user).exists()
#     return render (request , "courses/course-details.html" , {"course":course , "is_enrolled":is_enrolled})

# def course_details(request , id ):
#     course = get_object_or_404(Course,pk=id)
#     is_enrolled = False
#     if request.user.is_authenticated and request.user.profile.role == "student":
#         is_enrolled = Enrollment.objects.filter(course=course , student=request.user).exists()
#     return render (request , "courses/course-details.html" , {"course":course , "is_enrolled":is_enrolled})

def course_details(request , id ):
    course = get_object_or_404(Course,pk=id)
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            course=course, student=request.user
        ).exists()
    return render(
        request,
        "courses/course-details.html",
        {"course": course, "is_enrolled": is_enrolled},
    )


@login_required
@instructors_only
def instructor_courses(request):
    courses = Course.objects.filter(instructor=request.user)
    return render (request , "courses/instructor-courses.html" , {"courses":courses})


@login_required
@instructors_only
def create_course(request):
     form = CourseForm(request.POST or None)
     if form.is_valid():
         
        course =  form.save(commit=False)
        course.instructor = request.user
        course.save()
        messages.success(request , "Course created successfully")

        return redirect("instructor-courses")
         
     
     return render (request , "courses/create-course.html" , {"form":form}) 





@login_required
@instructors_only
def delete_course(request , id):
    course = get_object_or_404(Course,pk=id , instructor = request.user)

    if request.method == "POST":
          course.delete()
          messages.success(request , "Course Deleted Successfully")
          return redirect ("instructor-courses")
    return render(request , "courses/delete-confirmation.html" , {"title":course.title})



@login_required
@instructors_only
def edit_course(request,id):
     course = get_object_or_404(Course,pk=id, instructor = request.user)
         
     form = CourseForm(request.POST or None , instance=course)
     if form.is_valid():
         form.save()
         messages.success(request , "Course edited Successfully")
         
         return redirect("instructor-courses")
     return render (request , "courses/edit-course.html" , {"form" : form })



@login_required
@students_only
def enroll_course(request , id):
    course = get_object_or_404(Course, pk=id)
    try:
        Enrollment.objects.create(course=course,student=request.user)
        messages.success(request , "You  enrolled Successfully")

    except  IntegrityError :
        messages.error(request , "You has been enrolled this course before")
    finally:
          return redirect("student-enrollments")



@login_required
@students_only
def student_enrollments(request):
    enrollments = Enrollment.objects.filter(student = request.user)
    return render(request , "courses/student-enrollments.html" , {"enrollments":enrollments})


@login_required
@instructors_only
def course_documents(request, id):
    course = get_object_or_404(Course, pk=id, instructor=request.user)
    documents = course.documents.all()
    form = CourseDocumentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        doc = form.save(commit=False)
        doc.course = course
        doc.save()
        messages.success(request, "Document uploaded and indexed for the AI assistant.")
        return redirect("course-documents", id=course.id)
    return render(
        request,
        "courses/course-documents.html",
        {"course": course, "documents": documents, "form": form},
    )


@login_required
@students_only
def course_assistant(request, id):
    course = get_object_or_404(Course, pk=id)
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        raise PermissionDenied("You must be enrolled in this course to use the assistant.")

    chat_messages = ChatMessage.objects.filter(
        student=request.user, course=course
    ).order_by("created_at")

    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        if not message:
            messages.error(request, "Please enter a message.")
        elif not ai_configured():
            messages.error(request, "AI assistant is not configured. Set OPENROUTER_API_KEY in .env.")
        else:
            try:
                handle_chat(request.user, course, message)
            except Exception:
                messages.error(request, "Could not get a response from the assistant. Try again.")
        return redirect("course-assistant", id=course.id)

    return render(
        request,
        "courses/course-assistant.html",
        {"course": course, "chat_messages": chat_messages},
    )


@login_required
@students_only
def course_recommend(request):
    chat_messages = RecommendChatMessage.objects.filter(
        student=request.user
    ).order_by("created_at")
    return render(
        request,
        "courses/course-recommend.html",
        {"chat_messages": chat_messages},
    )


@login_required
@students_only
@require_POST
def course_recommend_send(request):
    message = request.POST.get("message", "").strip()
    if not message:
        return JsonResponse({"error": "Message cannot be empty."}, status=400)
    if not ai_configured():
        return JsonResponse(
            {"error": "AI recommender is not configured. Set OPENROUTER_API_KEY in .env."},
            status=503,
        )
    try:
        assistant_msg = handle_recommend_chat(request.user, message)
    except Exception as exc:
        return JsonResponse(
            {"error": f"Could not get a response: {exc}"},
            status=500,
        )

    user_msg = (
        RecommendChatMessage.objects.filter(
            student=request.user, role="user"
        )
        .order_by("-created_at")
        .first()
    )
    return JsonResponse(
        {
            "user_message": {
                "content": user_msg.content,
                "created_at": user_msg.created_at.strftime("%b %d, %H:%M"),
            },
            "assistant_message": {
                "id": assistant_msg.id,
                "content": assistant_msg.content,
                "recommendations_data": assistant_msg.recommendations_data,
                "created_at": assistant_msg.created_at.strftime("%b %d, %H:%M"),
            },
        }
    )




