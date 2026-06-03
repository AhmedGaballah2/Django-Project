import chromadb
from chromadb.config import Settings as ChromaSettings
from django.conf import settings

CATALOG_COLLECTION = "course_catalog"

_client = None


def get_chroma_client():
    global _client
    if _client is None:
        persist_dir = str(settings.CHROMA_PERSIST_DIR)
        _client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_collection(name: str):
    client = get_chroma_client()
    return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def course_docs_collection_name(course_id: int) -> str:
    return f"course_docs_{course_id}"
