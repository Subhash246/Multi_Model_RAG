from app.services.chunking.models import DocumentChunk
from app.services.pii.noop import NoOpPIIProvider
from app.services.pii.service import PIIProcessingService


def test_pii_service_processes_chunk():

    chunk = DocumentChunk(
        chunk_id="chunk-1",
        document_id="document-1",
        content="Employee information.",
        tenant_id="default",
        access_tags=["public"],
        page_start=1,
        page_end=1,
        metadata={
            "source": "parser",
        },
    )

    service = PIIProcessingService(
        provider=NoOpPIIProvider()
    )

    processed_chunk = service.process_chunk(
        chunk
    )

    assert processed_chunk.content == (
        "Employee information."
    )

    assert processed_chunk.metadata[
        "pii_detected"
    ] is False

    assert processed_chunk.metadata[
        "pii_entity_count"
    ] == 0