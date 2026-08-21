"""
Normalized chunk representations.

Chunks are the intermediate representation between
document parsing and downstream processing such as
PII handling and indexing.
"""

from dataclasses import dataclass, field
from typing import Any

from app.services.parsing.models import NormalizedDocument


@dataclass
class DocumentChunk:
    """
    Represents a searchable unit derived from a document.
    """

    chunk_id: str
    document_id: str
    content: str
    tenant_id: str
    access_tags: list[str] = field(default_factory=list)
    chunk_type: str = "page"

    parent_id: str | None = None

    page_start: int | None = None
    page_end: int | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

@dataclass
class ChunkedDocument:
    """
    Represents a normalized document together with the
    chunks produced from it.

    This is the intermediate representation between
    parsing/chunking and downstream processing such as
    PII handling, embeddings, and indexing.
    """

    document: NormalizedDocument
    chunks: list[DocumentChunk] = field(
        default_factory=list
    )

