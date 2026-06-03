from langchain_core.messages import HumanMessage, SystemMessage

from courses.models import Course, Enrollment

from .catalog_index import search_catalog
from .config import ai_configured
from .llm import get_chat_llm


def get_enrolled_course_ids(student) -> set[int]:
    return set(
        Enrollment.objects.filter(student=student).values_list("course_id", flat=True)
    )


def recommend_courses(query: str, student, top_n: int = 5) -> list[dict]:
    if not ai_configured():
        raise RuntimeError(
            "AI is not configured. Set OPENROUTER_API_KEY (or OPENAI_API_KEY) in your .env file."
        )

    enrolled_ids = get_enrolled_course_ids(student)
    try:
        hits = search_catalog(query, n_results=top_n + len(enrolled_ids))
    except Exception:
        hits = []

    recommendations = []
    for hit in hits:
        course_id = hit["course_id"]
        if course_id in enrolled_ids:
            continue
        try:
            course = Course.objects.select_related("category", "instructor").get(
                pk=course_id, is_published=True
            )
        except Course.DoesNotExist:
            continue
        explanation = _generate_explanation(query, course, hit.get("document", ""))
        recommendations.append(
            {
                "course": course,
                "explanation": explanation,
                "relevance_score": hit.get("distance"),
            }
        )
        if len(recommendations) >= top_n:
            break
    return recommendations


def _generate_explanation(query: str, course: Course, context: str) -> str:
    llm = get_chat_llm(temperature=0.3)
    system = (
        "You are a course advisor. Given a student query and course details, "
        "write one short sentence explaining why this course is a good match."
    )
    user_content = (
        f"Student query: {query}\n\n"
        f"Course: {course.title}\n"
        f"Category: {course.category.name}\n"
        f"Level: {course.get_level_display()}\n"
        f"Description: {course.description}\n\n"
        f"Catalog context:\n{context}"
    )
    response = llm.invoke(
        [SystemMessage(content=system), HumanMessage(content=user_content)]
    )
    return response.content.strip()
