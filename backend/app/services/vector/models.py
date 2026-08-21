"""
Provider-agnostic vector store representations.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VectorRecord:
    """
    Represents a vector together with the metadata required
    for storage and retrieval.
    """

    id: str
    vector: list[float]

    tenant_id: str

    document_id: str

    chunk_id: str

    content: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class VectorSearchResult:
    """
    Represents a vector search match.
    """

    id: str

    score: float

    tenant_id: str

    document_id: str

    chunk_id: str

    content: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )