"""
Embedding provider abstraction.

The indexing and retrieval pipelines depend on this interface
rather than a specific embedding model or library.
"""

from abc import ABC, abstractmethod

from app.services.embedding.models import EmbeddingResult


class BaseEmbeddingProvider(ABC):

    @abstractmethod
    def embed_text(
        self,
        text: str,
    ) -> EmbeddingResult:
        """
        Generate an embedding for a single text input.
        """
        raise NotImplementedError

    @abstractmethod
    def embed_documents(
        self,
        texts: list[str],
    ) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple document texts.
        """
        raise NotImplementedError

    @abstractmethod
    def embed_query(
        self,
        query: str,
    ) -> EmbeddingResult:
        """
        Generate an embedding for a user query.
        """
        raise NotImplementedError