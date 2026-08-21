"""
Fake vector store.

Used for testing the indexing and retrieval pipelines without
requiring a real vector database.

The implementation intentionally mirrors the important
behavior expected from a production vector store:

- tenant isolation
- cosine similarity scoring
- top-k ranking
- zero-vector safety
- vector dimension validation
- upsert semantics
- document-level deletion
"""

from math import sqrt

from app.services.vector.base import BaseVectorStore
from app.services.vector.models import (
    VectorRecord,
    VectorSearchResult,
)
from typing import Any


class FakeVectorStore(BaseVectorStore):
    """
    In-memory vector store used for development and testing.

    This is not intended to be a production vector database.
    It provides deterministic behavior that matches the contract
    expected by the indexing and retrieval layers.
    """

    def __init__(self) -> None:
        # Keyed by vector ID so upsert replaces existing records.
        self.records: dict[str, VectorRecord] = {}

    # ------------------------------------------------------------------
    # Upsert
    # ------------------------------------------------------------------

    def upsert(
        self,
        records: list[VectorRecord],
    ) -> None:
        """
        Insert or replace vector records.

        If a record with the same ID already exists, it is replaced.
        """

        for record in records:
            self.records[record.id] = record

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        *,
        tenant_id: str,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """
        Search vectors belonging to a tenant.

        Results are ranked using cosine similarity.

        Invalid vector dimensions are ignored rather than causing
        the entire search operation to fail.

        A zero query vector produces a score of 0.0 for every
        valid stored vector.
        """

        if top_k <= 0:
            return []

        results: list[VectorSearchResult] = []

        query_dimension = len(query_vector)

        for record in self.records.values():
            # ----------------------------------------------------------
            # Tenant isolation
            # ----------------------------------------------------------
            if record.tenant_id != tenant_id:
                continue

            # ----------------------------------------------------------
            # Metadata filtering
            # ----------------------------------------------------------
            if filters:
                if any(
                    record.metadata.get(key) != value
                    for key, value in filters.items()
                ):
                    continue

            # ----------------------------------------------------------
            # Dimension validation
            # ----------------------------------------------------------
            if len(record.vector) != query_dimension:
                continue

            # ----------------------------------------------------------
            # Similarity calculation
            # ----------------------------------------------------------
            score = self._cosine_similarity(
                query_vector,
                record.vector,
            )

            results.append(
                VectorSearchResult(
                    id=record.id,
                    score=score,
                    tenant_id=record.tenant_id,
                    document_id=record.document_id,
                    chunk_id=record.chunk_id,
                    content=record.content,
                    metadata=record.metadata,
                )
            )

        # --------------------------------------------------------------
        # Highest similarity first
        # --------------------------------------------------------------
        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(
        self,
        *,
        tenant_id: str,
        document_id: str,
    ) -> None:
        """
        Delete all vectors belonging to a document within a tenant.
        """

        self.records = {
            record_id: record
            for record_id, record in self.records.items()
            if not (
                record.tenant_id == tenant_id
                and record.document_id == document_id
            )
        }

    # ------------------------------------------------------------------
    # Cosine similarity
    # ------------------------------------------------------------------

    @staticmethod
    def _cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:
        """
        Calculate cosine similarity between two vectors.

        cosine_similarity =

            dot(a, b)
            -----------
            ||a|| * ||b||

        If either vector has zero magnitude, similarity is
        defined as 0.0.
        """

        magnitude_a = sqrt(
            sum(value * value for value in vector_a)
        )

        magnitude_b = sqrt(
            sum(value * value for value in vector_b)
        )

        # --------------------------------------------------------------
        # Zero-vector safety
        # --------------------------------------------------------------
        if magnitude_a == 0.0 or magnitude_b == 0.0:
            return 0.0

        dot_product = sum(
            a * b
            for a, b in zip(vector_a, vector_b)
        )

        return dot_product / (
            magnitude_a * magnitude_b
        )