from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import get_settings


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    return GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=settings.gemini_api_key,
    )