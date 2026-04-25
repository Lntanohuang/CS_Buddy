from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from app.config import settings


def get_embeddings() -> Embeddings:
    embedding_kwargs = {
        "model": "embedding-3",
        "api_key": settings.OPENAI_API_KEY,
    }
    if settings.OPENAI_BASE_URL:
        embedding_kwargs["base_url"] = settings.OPENAI_BASE_URL
    return OpenAIEmbeddings(**embedding_kwargs)
