"""
No-op PII provider.

Used when PII processing is disabled or
during early pipeline development.
"""

from app.services.pii.base import BasePIIProvider
from app.services.pii.models import PIIResult


class NoOpPIIProvider(BasePIIProvider):

    def process(self, text: str) -> PIIResult:

        return PIIResult(
            original_text=text,
            processed_text=text,
            entities=[],
        )