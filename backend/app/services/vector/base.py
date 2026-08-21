"""
Vector store abstraction.

The indexing and retrieval layers depend on this interface
rather than a specific vector database implementation.
"""

from abc import ABC, abstractmethod
from typing import Any

from app.services.vector.models import (
    VectorRecord,
    VectorSearchResult,
)


class BaseVectorStore(ABC):

    @abstractmethod
    def upsert(
        self,
        records: list[VectorRecord],
    ) -> None:
        """
        Insert or update vector records.
        """
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        *,
        tenant_id: str,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """
        Search vectors within a tenant boundary.

        Optional metadata filters can further restrict
        the searchable records.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        *,
        tenant_id: str,
        document_id: str,
    ) -> None:
        """
        Delete all vectors belonging to a document
        within a tenant.
        """
        raise NotImplementedError