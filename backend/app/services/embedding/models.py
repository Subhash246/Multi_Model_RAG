"""
Provider-agnostic embedding representations.
"""

from dataclasses import dataclass, field


@dataclass
class EmbeddingResult:
    """
    Represents an embedding generated for a piece of text.
    """

    vector: list[float]

    model: str

    dimensions: int

    metadata: dict[str, object] = field(
        default_factory=dict
    )