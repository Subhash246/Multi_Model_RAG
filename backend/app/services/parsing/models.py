"""
Normalized representations produced by document parsers.

All format-specific parsers convert their input into these
provider-agnostic structures.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParsedPage:
    """
    Represents the extracted content of a single document page.
    """

    page_number: int
    text: str
    content_type: str = "text"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class NormalizedDocument:
    """
    Provider-agnostic representation of a parsed document.

    This is the contract between parsing and downstream
    ingestion stages such as chunking and metadata processing.
    """

    document_id: str
    content_type: str
    pages: list[ParsedPage]

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    extraction: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def text(self) -> str:
        """
        Return complete document text while preserving
        page boundaries.
        """

        return "\n\n".join(
            f"[Page {page.page_number}]\n{page.text}"
            for page in self.pages
        )

    @property
    def page_count(self) -> int:
        """
        Number of pages in the normalized document.
        """

        return len(self.pages)

    @property
    def character_count(self) -> int:
        """
        Number of characters in the normalized document text.
        """

        return len(self.text)