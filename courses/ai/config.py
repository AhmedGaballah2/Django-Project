from django.conf import settings


def get_api_key():
    """OpenRouter keys work here; set OPENAI_API_KEY or OPENROUTER_API_KEY in .env."""
    return (
        getattr(settings, "OPENAI_API_KEY", "")
        or getattr(settings, "OPENROUTER_API_KEY", "")
        or ""
    )


def ai_configured():
    return bool(get_api_key())


# Backwards-compatible alias
def get_openai_api_key():
    return get_api_key()
