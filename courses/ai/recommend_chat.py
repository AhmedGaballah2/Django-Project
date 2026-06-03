import re

from django.db.models import Q
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from courses.models import Course, Enrollment, RecommendChatMessage

from .config import ai_configured
from .llm import get_chat_llm
from .recommender import get_enrolled_course_ids, recommend_courses

CHAT_HISTORY_LIMIT = 20

SMALLTALK_EXACT = {
    "hi",
    "hello",
    "hey",
    "hola",
    "thanks",
    "thank you",
    "bye",
    "goodbye",
    "good morning",
    "good evening",
    "how are you",
    "what's up",
    "whats up",
}

COURSE_INQUIRY_KEYWORDS = (
    "course",
    "courses",
    "learn",
    "learning",
    "study",
    "class",
    "enroll",
    "recommend",
    "suggestion",
    "suggest",
    "beginner",
    "intermediate",
    "advanced",
    "python",
    "javascript",
    "web",
    "design",
    "business",
    "programming",
    "topic",
    "skill",
    "want to",
    "looking for",
    "interested in",
    "teach me",
    "help me find",
)


def _is_smalltalk(message: str) -> bool:
    text = message.lower().strip()
    if text in SMALLTALK_EXACT:
        return True
    if re.match(r"^(hi|hello|hey|thanks|thank you|bye|goodbye)\b", text):
        return True
    return False


def _is_course_inquiry(message: str) -> bool:
    if _is_smalltalk(message):
        return False
    lower = message.lower()
    return any(keyword in lower for keyword in COURSE_INQUIRY_KEYWORDS)


def _conversation_mentions_learning(prior_messages: list[RecommendChatMessage]) -> bool:
    for msg in prior_messages[-6:]:
        if msg.role == "user" and _is_course_inquiry(msg.content):
            return True
    return False


def _get_prior_messages(student, exclude_last: bool = True) -> list[RecommendChatMessage]:
    qs = RecommendChatMessage.objects.filter(student=student).order_by("created_at")
    messages = list(qs)
    if exclude_last and messages:
        messages = messages[:-1]
    return messages[-CHAT_HISTORY_LIMIT:]


def _history_to_langchain(messages: list[RecommendChatMessage]) -> list:
    turns = []
    for msg in messages:
        if msg.role == "user":
            turns.append(HumanMessage(content=msg.content))
        else:
            turns.append(AIMessage(content=msg.content))
    return turns


def _build_catalog_context(student) -> str:
    enrolled = get_enrolled_course_ids(student)
    courses = (
        Course.objects.filter(is_published=True)
        .exclude(id__in=enrolled)
        .select_related("category", "instructor")
        .order_by("title")[:40]
    )
    if not courses:
        return "No published courses are currently available in the catalog."
    lines = []
    for course in courses:
        lines.append(
            f"- {course.title} | {course.category.name} | {course.get_level_display()} | "
            f"Instructor: {course.instructor.username} | {course.description[:180]}"
        )
    return "\n".join(lines)


def _db_fallback_matches(query: str, student, top_n: int = 3) -> list[dict]:
    enrolled = get_enrolled_course_ids(student)
    base = (
        Course.objects.filter(is_published=True)
        .exclude(id__in=enrolled)
        .select_related("category", "instructor")
    )
    if not base.exists():
        return []

    tokens = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2]
    qs = base
    if tokens:
        for token in tokens[:6]:
            qs = qs.filter(
                Q(title__icontains=token)
                | Q(description__icontains=token)
                | Q(category__name__icontains=token)
            )

    courses = list(qs.distinct()[:top_n])
    if not courses:
        courses = list(base[:top_n])

    return [
        {
            "course": course,
            "explanation": (
                f"This {course.get_level_display().lower()} course in "
                f"{course.category.name} may fit what you are looking for."
            ),
            "relevance_score": None,
        }
        for course in courses
    ]


def find_course_matches(query: str, student, top_n: int = 3) -> list[dict]:
    results = []
    if ai_configured():
        try:
            results = recommend_courses(query, student, top_n=top_n)
        except Exception:
            results = []
    if not results:
        results = _db_fallback_matches(query, student, top_n=top_n)
    return results


def _serialize_recommendation(course: Course, explanation: str) -> dict:
    return {
        "course_id": course.id,
        "title": course.title,
        "category": course.category.name,
        "level": course.get_level_display(),
        "instructor": course.instructor.username,
        "explanation": explanation,
    }


def _format_matches_for_prompt(matches: list[dict]) -> str:
    if not matches:
        return "No specific course matches for this turn."
    lines = []
    for item in matches:
        course = item["course"]
        lines.append(
            f"- {course.title} ({course.category.name}, {course.get_level_display()}): "
            f"{item['explanation']}"
        )
    return "\n".join(lines)


def _generate_conversational_reply(
    student,
    message: str,
    prior_messages: list[RecommendChatMessage],
    matches: list[dict],
) -> str:
    llm = get_chat_llm(temperature=0.75)
    catalog = _build_catalog_context(student)
    matches_text = _format_matches_for_prompt(matches)

    system = f"""You are a warm, helpful course advisor chatbot on an online learning platform.

Your personality:
- Friendly and natural — respond to greetings, thanks, and casual chat like a real assistant.
- Remember what the student said earlier in this conversation and refer back when relevant.
- When they ask about learning goals or courses, use the catalog and match list below.
- If SEMANTIC MATCHES are provided, mention those courses naturally in your reply (do not invent course names).
- If they only say hello, greet them and briefly explain you can help find courses — do not push courses aggressively.
- Keep replies concise (1–4 short paragraphs). Use plain text, no markdown headers.
- Never reply with only "I could not find courses" — if nothing matches, suggest they browse the catalog or describe their goal differently.

PUBLISHED COURSES (student is not enrolled in these yet):
{catalog}

SEMANTIC MATCHES for this message (may be empty):
{matches_text}
"""

    lc_messages = [SystemMessage(content=system)]
    lc_messages.extend(_history_to_langchain(prior_messages))
    lc_messages.append(HumanMessage(content=message))

    response = llm.invoke(lc_messages)
    return response.content.strip()


def handle_recommend_chat(student, message: str) -> RecommendChatMessage:
    if not ai_configured():
        raise RuntimeError(
            "AI is not configured. Set OPENROUTER_API_KEY (or OPENAI_API_KEY) in your .env file."
        )

    RecommendChatMessage.objects.create(student=student, role="user", content=message)

    prior_messages = _get_prior_messages(student, exclude_last=True)

    should_suggest = _is_course_inquiry(message) or _conversation_mentions_learning(
        prior_messages
    )
    matches = find_course_matches(message, student, top_n=3) if should_suggest else []

    content = _generate_conversational_reply(student, message, prior_messages, matches)

    recommendations_data = [
        _serialize_recommendation(item["course"], item["explanation"]) for item in matches
    ]

    return RecommendChatMessage.objects.create(
        student=student,
        role="assistant",
        content=content,
        recommendations_data=recommendations_data,
    )
