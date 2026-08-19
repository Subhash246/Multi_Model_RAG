"""
PII processing service.

Applies PII processing to document chunks.
"""

from app.services.chunking.models import DocumentChunk
from app.services.pii.base import BasePIIProvider


class PIIProcessingService:

    def __init__(
        self,
        provider: BasePIIProvider,
    ) -> None:

        self.provider = provider

    def process_chunk(
        self,
        chunk: DocumentChunk,
    ) -> DocumentChunk:

        result = self.provider.process(
            chunk.content
        )

        chunk.content = result.processed_text

        chunk.metadata["pii_detected"] = (
            result.detected
        )

        chunk.metadata["pii_entity_count"] = (
            len(result.entities)
        )

        return chunk