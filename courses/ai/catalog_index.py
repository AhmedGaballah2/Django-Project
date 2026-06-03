from courses.models import Course

from .config import ai_configured
from .embeddings import embed_texts
from .vector_store import CATALOG_COLLECTION, get_collection


def _course_document_text(course: Course) -> str:
    return (
        f"Title: {course.title}\n"
        f"Description: {course.description}\n"
        f"Category: {course.category.name}\n"
        f"Level: {course.get_level_display()}"
    )


def index_course(course: Course):
    if not course.is_published or not ai_configured():
        remove_course_from_index(course.id)
        return

    collection = get_collection(CATALOG_COLLECTION)
    text = _course_document_text(course)
    embedding = embed_texts([text])[0]
    doc_id = f"course_{course.id}"
    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[
            {
                "course_id": course.id,
                "title": course.title,
                "category": course.category.slug,
                "level": course.level,
            }
        ],
    )


def remove_course_from_index(course_id: int):
    collection = get_collection(CATALOG_COLLECTION)
    doc_id = f"course_{course_id}"
    try:
        collection.delete(ids=[doc_id])
    except Exception:
        pass


def search_catalog(query: str, n_results: int = 5) -> list[dict]:
    from .embeddings import embed_query

    collection = get_collection(CATALOG_COLLECTION)
    query_embedding = embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    items = []
    if not results["ids"] or not results["ids"][0]:
        return items
    for i, doc_id in enumerate(results["ids"][0]):
        meta = results["metadatas"][0][i] if results["metadatas"] else {}
        items.append(
            {
                "course_id": int(meta.get("course_id", 0)),
                "title": meta.get("title", ""),
                "distance": results["distances"][0][i] if results["distances"] else None,
                "document": results["documents"][0][i] if results["documents"] else "",
            }
        )
    return items


def reindex_all_published():
    if not ai_configured():
        return
    for course in Course.objects.filter(is_published=True).select_related("category"):
        index_course(course)
