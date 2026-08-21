from app.services.embedding.fake import FakeEmbeddingProvider
from app.services.retrieval.service import RetrievalService
from app.services.vector.fake import FakeVectorStore
from app.services.vector.models import VectorRecord


def test_retrieval_returns_tenant_scoped_results():

    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()

    vector_store.upsert(
        [
            VectorRecord(
                id="chunk-a",
                vector=[0.1, 0.2, 0.3],
                tenant_id="tenant-a",
                document_id="document-a",
                chunk_id="chunk-a",
                content="Tenant A document content.",
                metadata={},
            ),
            VectorRecord(
                id="chunk-b",
                vector=[0.1, 0.2, 0.3],
                tenant_id="tenant-b",
                document_id="document-b",
                chunk_id="chunk-b",
                content="Tenant B document content.",
                metadata={},
            ),
        ]
    )

    service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    results = service.retrieve(
        query="document content",
        tenant_id="tenant-a",
        top_k=5,
    )

    assert len(results) == 1
    assert results[0].tenant_id == "tenant-a"
    assert results[0].chunk_id == "chunk-a"


def test_retrieval_returns_empty_for_blank_query():

    service = RetrievalService(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=FakeVectorStore(),
    )

    results = service.retrieve(
        query="   ",
        tenant_id="tenant-a",
        top_k=5,
    )

    assert results == []


def test_retrieval_returns_empty_for_invalid_top_k():

    service = RetrievalService(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=FakeVectorStore(),
    )

    results = service.retrieve(
        query="hello",
        tenant_id="tenant-a",
        top_k=0,
    )

    assert results == []