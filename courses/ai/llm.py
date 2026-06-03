from django.conf import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .config import get_api_key


def _openrouter_headers():
    return {
        "HTTP-Referer": getattr(settings, "OPENROUTER_SITE_URL", "http://127.0.0.1:8000"),
        "X-Title": getattr(settings, "OPENROUTER_APP_NAME", "Courses Platform"),
    }


def get_chat_llm(*, temperature: float = 0.4) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.OPENAI_CHAT_MODEL,
        api_key=get_api_key(),
        base_url=settings.OPENAI_API_BASE,
        temperature=temperature,
        default_headers=_openrouter_headers(),
    )


def get_embeddings_client() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        api_key=get_api_key(),
        base_url=settings.OPENAI_API_BASE,
        default_headers=_openrouter_headers(),
    )
