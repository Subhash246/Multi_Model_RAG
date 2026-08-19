"""
Chunking provider abstraction.

The ingestion pipeline depends on this interface rather
than a specific chunking implementation.
"""

from abc import ABC, abstractmethod

from app.services.chunking.models import DocumentChunk
from app.services.parsing.models import NormalizedDocument


class BaseChunker(ABC):

    @abstractmethod
    def chunk(
        self,
        document: NormalizedDocument,
    ) -> list[DocumentChunk]:
        """
        Convert a normalized document into document chunks.
        """

        raise NotImplementedError