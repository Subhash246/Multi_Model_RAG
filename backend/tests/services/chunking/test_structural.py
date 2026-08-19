from app.services.chunking.models import DocumentChunk
from app.services.chunking.structural import StructuralChunker
from app.services.parsing.models import (
    NormalizedDocument,
    ParsedPage,
)


def test_structural_chunker_creates_page_chunks():

    document = NormalizedDocument(
        document_id="document-123",
        content_type="application/pdf",
        pages=[
            ParsedPage(
                page_number=1,
                text="First page content.",
            ),
            ParsedPage(
                page_number=2,
                text="Second page content.",
            ),
        ],
    )

    chunker = StructuralChunker()

    chunks = chunker.chunk(document)

    assert len(chunks) == 2

    assert all(
        isinstance(chunk, DocumentChunk)
        for chunk in chunks
    )

    assert chunks[0].document_id == "document-123"

    assert chunks[0].content == "First page content."

    assert chunks[0].page_start == 1
    assert chunks[0].page_end == 1

    assert chunks[1].page_start == 2
    assert chunks[1].page_end == 2

    assert chunks[0].chunk_type == "page"
    assert chunks[1].chunk_type == "page"