"""
Parser provider abstraction.

The ingestion layer depends on this interface rather than
individual parsing libraries.
"""

from abc import ABC, abstractmethod

from app.services.parsing.models import NormalizedDocument


class BaseParser(ABC):

    @abstractmethod
    def parse(
        self,
        file_data: bytes,
        content_type: str,
        document_id: str,
    ) -> NormalizedDocument:
        """
        Parse raw file bytes into a normalized document.
        """

        raise NotImplementedError