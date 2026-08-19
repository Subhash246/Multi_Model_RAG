"""
PII detection and redaction provider abstraction.
"""

from abc import ABC, abstractmethod

from app.services.pii.models import PIIResult


class BasePIIProvider(ABC):

    @abstractmethod
    def process(self, text: str) -> PIIResult:
        """
        Detect and/or redact sensitive information
        from the supplied text.
        """

        raise NotImplementedError