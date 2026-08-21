from app.services.chunking.models import DocumentChunk
from app.services.embedding.fake import FakeEmbeddingProvider
from app.services.indexing import IndexingService
from app.services.vector.fake import FakeVectorStore


def test_indexing_service_creates_vector_records():

    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()

    indexing_service = IndexingService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    chunks = [
        DocumentChunk(
            chunk_id="chunk-1",
            document_id="document-1",
            content="Hello world",
            tenant_id="tenant-a",
            access_tags=["tenant:tenant-a"],
        ),
        DocumentChunk(
            chunk_id="chunk-2",
            document_id="document-1",
            content="Second chunk",
            tenant_id="tenant-a",
            access_tags=["tenant:tenant-a"],
        ),
    ]

    indexing_service.index_chunks(chunks)

    assert len(vector_store.records) == 2

    assert vector_store.records["chunk-1"].chunk_id == "chunk-1"
    assert vector_store.records["chunk-2"].chunk_id == "chunk-2"

    assert vector_store.records["chunk-1"].tenant_id == "tenant-a"

    assert (
        vector_store.records["chunk-1"].metadata["embedding_model"]
        == "fake-model"
    )

    assert (
        vector_store.records["chunk-1"].metadata["embedding_dimensions"]
        == 3
    )

def test_indexing_preserves_tenant_boundary():

    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()

    indexing_service = IndexingService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    chunks = [
        DocumentChunk(
            chunk_id="chunk-a",
            document_id="document-a",
            content="Tenant A data",
            tenant_id="tenant-a",
        ),
        DocumentChunk(
            chunk_id="chunk-b",
            document_id="document-b",
            content="Tenant B data",
            tenant_id="tenant-b",
        ),
    ]

    indexing_service.index_chunks(chunks)

    results = vector_store.search(
        tenant_id="tenant-a",
        query_vector=[0.1, 0.2, 0.3],
        top_k=10,
    )

    assert len(results) == 1
    assert results[0].tenant_id == "tenant-a"
    assert results[0].chunk_id == "chunk-a"