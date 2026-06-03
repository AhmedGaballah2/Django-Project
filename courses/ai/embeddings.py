from .llm import get_embeddings_client


def embed_texts(texts: list[str]) -> list[list[float]]:
    return get_embeddings_client().embed_documents(texts)


def embed_query(text: str) -> list[float]:
    return get_embeddings_client().embed_query(text)
