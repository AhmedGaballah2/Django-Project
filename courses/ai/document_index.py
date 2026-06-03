import os

from pypdf import PdfReader

from .chunking import split_text
from .config import ai_configured
from .embeddings import embed_texts
from .vector_store import course_docs_collection_name, get_collection


def extract_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(file_path)
        parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
        return "\n".join(parts)
    if ext in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    raise ValueError(f"Unsupported file type: {ext}. Use PDF or .txt files.")


def index_course_document(document):
    if not ai_configured():
        return

    file_path = document.file.path
    text = extract_text_from_file(file_path)
    chunks = split_text(text)
    if not chunks:
        return

    collection_name = course_docs_collection_name(document.course_id)
    collection = get_collection(collection_name)
    embeddings = embed_texts(chunks)
    ids = [f"doc_{document.id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "document_id": document.id,
            "document_title": document.title,
            "course_id": document.course_id,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )


def remove_course_document_from_index(document):
    collection_name = course_docs_collection_name(document.course_id)
    collection = get_collection(collection_name)
    try:
        existing = collection.get(where={"document_id": document.id})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass


def search_course_documents(course_id: int, query: str, n_results: int = 4) -> list[dict]:
    from .embeddings import embed_query

    collection_name = course_docs_collection_name(course_id)
    collection = get_collection(collection_name)
    query_embedding = embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    items = []
    if not results["ids"] or not results["ids"][0]:
        return items
    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i] if results["metadatas"] else {}
        items.append(
            {
                "text": results["documents"][0][i] if results["documents"] else "",
                "document_title": meta.get("document_title", ""),
                "chunk_index": meta.get("chunk_index", 0),
            }
        )
    return items
