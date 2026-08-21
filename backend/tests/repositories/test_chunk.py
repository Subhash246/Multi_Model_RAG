from app.core.database import SessionLocal
from app.repositories.chunk import ChunkRepository
from app.services.chunking.models import DocumentChunk
from app.models.chunk import Chunk
from app.models.document import Document


def test_chunk_repository_creates_chunks():

    db = SessionLocal()

    document_id = "9241c403-39f7-473e-aaf7-f98275ebe9e9"

    try:
        document = Document(
            id=document_id,
            tenant_id="default",
            filename="test.pdf",
            content_type="application/pdf",
            size_bytes=100,
            storage_key="test-repository.pdf",
            status="uploaded",
        )

        db.add(document)
        db.commit()

        chunks = [
            DocumentChunk(
                chunk_id="test-chunk-1",
                document_id=document_id,
                content="First test chunk.",
                tenant_id="default",
                page_start=1,
                page_end=1,
                metadata={
                    "source": "test",
                    "page_number": 1,
                },
            ),
            DocumentChunk(
                chunk_id="test-chunk-2",
                document_id=document_id,
                content="Second test chunk.",
                tenant_id="default",
                page_start=2,
                page_end=2,
                metadata={
                    "source": "test",
                    "page_number": 2,
                },
            ),
        ]

        repository = ChunkRepository(db)

        db_chunks = repository.create_many(chunks)

        assert len(db_chunks) == 2
        assert db_chunks[0].id == "test-chunk-1"
        assert db_chunks[0].document_id == document_id
        assert db_chunks[1].id == "test-chunk-2"
        assert db_chunks[1].page_start == 2

    finally:
        db.rollback()

        db.query(Chunk).filter(
            Chunk.id.in_([
                "test-chunk-1",
                "test-chunk-2",
            ])
        ).delete(
            synchronize_session=False
        )

        db.query(Document).filter(
            Document.id == document_id
        ).delete(
            synchronize_session=False
        )

        db.commit()
        db.close()