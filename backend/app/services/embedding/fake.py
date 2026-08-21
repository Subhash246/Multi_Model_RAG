"""
Fake embedding provider.

Used for testing the indexing and retrieval pipelines
without loading a real embedding model or library.
"""

from app.services.embedding.base import BaseEmbeddingProvider
from app.services.embedding.models import EmbeddingResult


class FakeEmbeddingProvider(BaseEmbeddingProvider):

    def __init__(self) -> None:
        self.model = "fake-model"
        self.dimensions = 3

    def embed_text(
        self,
        text: str,
    ) -> EmbeddingResult:
        return EmbeddingResult(
            vector=[0.1, 0.2, 0.3],
            model=self.model,
            dimensions=self.dimensions,
            metadata={
                "provider": "fake",
            },
        )

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[EmbeddingResult]:
        return [
            self.embed_text(text)
            for text in texts
        ]

    def embed_query(
        self,
        query: str,
    ) -> EmbeddingResult:
        return self.embed_text(query)