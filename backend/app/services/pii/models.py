"""
PII processing representations.
"""

from dataclasses import dataclass, field


@dataclass
class PIIEntity:
    entity_type: str
    start: int
    end: int
    score: float


@dataclass
class PIIResult:
    original_text: str
    processed_text: str
    entities: list[PIIEntity] = field(
        default_factory=list
    )

    @property
    def detected(self) -> bool:
        return bool(self.entities)