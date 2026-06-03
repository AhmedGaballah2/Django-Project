from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from courses.models import ChatMessage, Course

from .config import ai_configured
from .document_index import search_course_documents
from .llm import get_chat_llm


CHAT_HISTORY_LIMIT = 10


def get_chat_history(student, course, limit: int = CHAT_HISTORY_LIMIT) -> list[dict]:
    messages = ChatMessage.objects.filter(student=student, course=course).order_by(
        "-created_at"
    )[:limit]
    return list(reversed([{"role": m.role, "content": m.content} for m in messages]))


def _course_context(course: Course) -> str:
    return (
        f"Course: {course.title}\n"
        f"Category: {course.category.name}\n"
        f"Level: {course.get_level_display()}\n"
        f"Description: {course.description}"
    )


def route_question(message: str, course: Course) -> str:
    """Orchestrator: returns 'rag' or 'general'."""
    llm = get_chat_llm()
    system = (
        "You are a router for a course teaching assistant. "
        "Reply with exactly one word: 'rag' if the question should be answered "
        "using uploaded course documents (lecture notes, slides, readings, assignments), "
        "or 'general' if it is about the subject broadly and does not require document content."
    )
    response = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(
                content=f"{_course_context(course)}\n\nStudent question: {message}"
            ),
        ]
    )
    choice = response.content.strip().lower()
    return "rag" if "rag" in choice else "general"


def rag_agent_answer(message: str, course: Course, history: list[dict]) -> tuple[str, list[str]]:
    chunks = search_course_documents(course.id, message, n_results=4)
    sources = []
    context_parts = []
    for c in chunks:
        label = f"{c['document_title']} (chunk {c['chunk_index']})"
        sources.append(label)
        context_parts.append(f"[{label}]\n{c['text']}")

    context_block = "\n\n".join(context_parts) if context_parts else "No relevant document chunks found."
    llm = get_chat_llm()
    system = (
        "You are a teaching assistant. Answer ONLY using the provided course document excerpts. "
        "If the excerpts do not contain enough information, say so clearly. "
        "Cite which source labels you used."
    )
    messages = [SystemMessage(content=f"{_course_context(course)}\n\nDocument excerpts:\n{context_block}")]
    for turn in history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=message))

    response = llm.invoke(messages)
    answer = response.content.strip()
    if not sources:
        answer += "\n\n(No matching course materials were found in the knowledge base.)"
    return answer, sources


def general_agent_answer(message: str, course: Course, history: list[dict]) -> str:
    llm = get_chat_llm()
    system = (
        "You are a helpful teaching assistant for the course described below. "
        "Answer using general knowledge about the subject. "
        "Clearly state that your answer is based on general knowledge, not uploaded course materials."
    )
    messages = [SystemMessage(content=_course_context(course))]
    for turn in history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=message))
    response = llm.invoke(messages)
    return response.content.strip()


def handle_chat(student, course: Course, message: str) -> dict:
    if not ai_configured():
        raise RuntimeError(
            "AI is not configured. Set OPENROUTER_API_KEY (or OPENAI_API_KEY) in your .env file."
        )

    history = get_chat_history(student, course)
    route = route_question(message, course)

    if route == "rag":
        answer, sources = rag_agent_answer(message, course, history)
        source_tag = "RAG"
        source_refs = sources
    else:
        answer = general_agent_answer(message, course, history)
        source_tag = "General"
        source_refs = ["general knowledge"]

    ChatMessage.objects.create(
        student=student, course=course, role="user", content=message
    )
    ChatMessage.objects.create(
        student=student,
        course=course,
        role="assistant",
        content=answer,
        source=source_tag,
    )

    return {
        "response": answer,
        "source": source_tag,
        "source_references": source_refs,
        "route": route,
    }
