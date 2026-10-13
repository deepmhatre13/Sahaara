import logging

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
try:
    from langchain_qdrant import QdrantVectorStore
except ImportError:
    QdrantVectorStore = None

from app.core.config import get_settings
from app.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)

_EMBEDDING_DIM = 768  # Gemini "models/embedding-001" output dimension


def get_qdrant_client() -> QdrantClient:
    settings = get_settings()
    return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)


def ensure_collection(client: QdrantClient) -> None:
    settings = get_settings()
    collections = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in collections:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=_EMBEDDING_DIM, distance=Distance.COSINE),
        )
        logger.info("Created Qdrant collection '%s'", settings.qdrant_collection)


def get_vector_store() -> QdrantVectorStore:
    settings = get_settings()
    client = get_qdrant_client()
    ensure_collection(client)
    return QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
        embedding=get_embeddings(),
    )