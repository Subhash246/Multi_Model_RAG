"""
Retrieval service.

Converts a user query into an embedding and retrieves
tenant-scoped vector records from the configured vector store.
"""

from app.services.embedding.base import BaseEmbeddingProvider
from app.services.vector.base import BaseVectorStore
from app.services.vector.models import VectorRecord


class RetrievalService:
    """
    Application service responsible for semantic retrieval.

    The service is provider-agnostic:
    - embedding provider can be replaced independently
    - vector store can be replaced independently
    """

    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: BaseVectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        tenant_id: str,
        top_k: int = 5,
    ) -> list[VectorRecord]:
        """
        Retrieve the most relevant chunks for a tenant-scoped query.
        """

        if not query.strip():
            return []

        if top_k <= 0:
            return []

        query_embedding = self.embedding_provider.embed_query(query)

        return self.vector_store.search(
            tenant_id=tenant_id,
            query_vector=query_embedding.vector,
            top_k=top_k,
        )