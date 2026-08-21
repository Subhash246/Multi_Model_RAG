from app.services.chunking.models import ChunkedDocument
from app.services.chunking.structural import StructuralChunker
from app.services.ingestion import DocumentIngestionService
from app.services.parsing.models import (
    NormalizedDocument,
    ParsedPage,
)
from app.services.pii.noop import NoOpPIIProvider
from app.services.pii.service import PIIProcessingService
from app.services.security.context import SecurityContext

class FakeStorage:

    def download(self, storage_key: str) -> bytes:
        return b"fake-pdf-data"


class FakeParser:

    def parse(
        self,
        file_data: bytes,
        content_type: str,
        document_id: str,
    ) -> NormalizedDocument:

        return NormalizedDocument(
            document_id=document_id,
            content_type=content_type,
            pages=[
                ParsedPage(
                    page_number=1,
                    text="First page.",
                ),
                ParsedPage(
                    page_number=2,
                    text="Second page.",
                ),
            ],
        )


class FakeParserRouter:

    def get_parser(self, content_type: str):
        return FakeParser()


class FakeChunkRepository:

    def __init__(self):
        self.created_chunks = []

    def create_many(self, chunks):
        self.created_chunks.extend(chunks)
        return chunks

class FakeIndexingService:
    def __init__(self):
        self.indexed_chunks = []

    def index_chunks(self, chunks):
        self.indexed_chunks.extend(chunks)

def test_ingestion_service_parses_chunks_processes_pii_and_persists():

    repository = FakeChunkRepository()

    pii_service = PIIProcessingService(
        provider=NoOpPIIProvider()
    )
    indexing_service = FakeIndexingService()

    service = DocumentIngestionService(
        storage=FakeStorage(),
        parser_router=FakeParserRouter(),
        chunker=StructuralChunker(),
        pii_service=pii_service,
        chunk_repository=repository,
        indexing_service=indexing_service,
    )

    from app.models.document import Document

    document = Document(
        id="document-123",
        tenant_id="default",
        filename="test.pdf",
        content_type="application/pdf",
        size_bytes=100,
        storage_key="test.pdf",
        status="uploaded",
    )

    security_context = SecurityContext(
        tenant_id="default",
        user_id="test-user",
        roles=["user"],
        permissions=["document:write"],
    )

    result = service.process_document(
        document=document,
        security_context=security_context,
    )

    assert isinstance(result, ChunkedDocument)

    assert result.document.document_id == "document-123"

    assert result.document.page_count == 2

    assert len(result.chunks) == 2

    assert result.chunks[0].content == "First page."
    assert result.chunks[1].content == "Second page."

    # PII metadata was added
    assert result.chunks[0].metadata["pii_detected"] is False
    assert result.chunks[0].metadata["pii_entity_count"] == 0

    assert result.chunks[1].metadata["pii_detected"] is False
    assert result.chunks[1].metadata["pii_entity_count"] == 0

    # Processed chunks were persisted
    assert len(repository.created_chunks) == 2
    assert indexing_service.indexed_chunks[0].chunk_id == result.chunks[0].chunk_id
    assert indexing_service.indexed_chunks[1].chunk_id == result.chunks[1].chunk_id