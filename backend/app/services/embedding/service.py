"""
Embedding service.

Coordinates embedding generation without depending on a
specific embedding model or provider.
"""

from app.services.embedding.base import BaseEmbeddingProvider
from app.services.embedding.models import EmbeddingResult


class EmbeddingService:

    def __init__(
        self,
        provider: BaseEmbeddingProvider,
    ) -> None:
        self.provider = provider

    def embed_text(
        self,
        text: str,
    ) -> EmbeddingResult:
        return self.provider.embed_text(text)

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[EmbeddingResult]:
        return self.provider.embed_documents(texts)