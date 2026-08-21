from app.services.vector.base import BaseVectorStore
from app.services.vector.models import (
    VectorRecord,
    VectorSearchResult,
)
from app.services.vector.fake import FakeVectorStore
from app.services.vector.models import VectorRecord


def test_vector_store_upsert_and_search():

    store = FakeVectorStore()

    store.upsert(
        [
            VectorRecord(
                id="vector-1",
                vector=[0.1, 0.2, 0.3],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-1",
                content="Hello world",
            )
        ]
    )

    results = store.search(
        tenant_id="tenant-a",
        query_vector=[0.1, 0.2, 0.3],
        top_k=5,
    )

    assert len(results) == 1
    assert results[0].chunk_id == "chunk-1"


def test_vector_store_enforces_tenant_boundary():

    store = FakeVectorStore()

    store.upsert(
        [
            VectorRecord(
                id="vector-1",
                vector=[0.1, 0.2, 0.3],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-1",
                content="Tenant A content",
            ),
            VectorRecord(
                id="vector-2",
                vector=[0.1, 0.2, 0.3],
                tenant_id="tenant-b",
                document_id="document-2",
                chunk_id="chunk-2",
                content="Tenant B content",
            ),
        ]
    )

    results = store.search(
        tenant_id="tenant-a",
        query_vector=[0.1, 0.2, 0.3],
        top_k=10,
    )

    assert len(results) == 1
    assert results[0].tenant_id == "tenant-a"
    assert results[0].chunk_id == "chunk-1"


def test_vector_store_delete_document():

    store = FakeVectorStore()

    store.upsert(
        [
            VectorRecord(
                id="vector-1",
                vector=[0.1, 0.2, 0.3],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-1",
                content="Document 1",
            ),
            VectorRecord(
                id="vector-2",
                vector=[0.4, 0.5, 0.6],
                tenant_id="tenant-a",
                document_id="document-2",
                chunk_id="chunk-2",
                content="Document 2",
            ),
        ]
    )

    store.delete(
        tenant_id="tenant-a",
        document_id="document-1",
    )

    results = store.search(
        tenant_id="tenant-a",
        query_vector=[0.1, 0.2, 0.3],
        top_k=10,
    )

    assert len(results) == 1
    assert results[0].document_id == "document-2"


# ------------------------------------------------------------------
# New retrieval tests
# ------------------------------------------------------------------


def test_vector_store_ranks_by_cosine_similarity():

    store = FakeVectorStore()

    store.upsert(
        [
            VectorRecord(
                id="vector-exact",
                vector=[1.0, 0.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-exact",
                content="Exact match",
            ),
            VectorRecord(
                id="vector-similar",
                vector=[0.8, 0.2, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-similar",
                content="Similar match",
            ),
            VectorRecord(
                id="vector-different",
                vector=[0.0, 1.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-different",
                content="Different match",
            ),
        ]
    )

    results = store.search(
        tenant_id="tenant-a",
        query_vector=[1.0, 0.0, 0.0],
        top_k=3,
    )

    assert len(results) == 3

    assert results[0].chunk_id == "chunk-exact"
    assert results[1].chunk_id == "chunk-similar"
    assert results[2].chunk_id == "chunk-different"

    assert results[0].score > results[1].score
    assert results[1].score > results[2].score


def test_vector_store_respects_top_k():

    store = FakeVectorStore()

    store.upsert(
        [
            VectorRecord(
                id="vector-1",
                vector=[1.0, 0.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-1",
                content="Content 1",
            ),
            VectorRecord(
                id="vector-2",
                vector=[0.9, 0.1, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-2",
                content="Content 2",
            ),
            VectorRecord(
                id="vector-3",
                vector=[0.8, 0.2, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-3",
                content="Content 3",
            ),
        ]
    )

    results = store.search(
        tenant_id="tenant-a",
        query_vector=[1.0, 0.0, 0.0],
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].chunk_id == "chunk-1"
    assert results[1].chunk_id == "chunk-2"


def test_vector_store_handles_zero_vector():

    store = FakeVectorStore()

    store.upsert(
        [
            VectorRecord(
                id="vector-1",
                vector=[1.0, 0.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-1",
                content="Content",
            )
        ]
    )

    results = store.search(
        tenant_id="tenant-a",
        query_vector=[0.0, 0.0, 0.0],
        top_k=10,
    )

    assert len(results) == 1
    assert results[0].score == 0.0


def test_vector_store_ignores_dimension_mismatch():

    store = FakeVectorStore()

    store.upsert(
        [
            VectorRecord(
                id="vector-valid",
                vector=[1.0, 0.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-valid",
                content="Valid vector",
            ),
            VectorRecord(
                id="vector-invalid",
                vector=[1.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-invalid",
                content="Invalid dimension",
            ),
        ]
    )

    results = store.search(
        tenant_id="tenant-a",
        query_vector=[1.0, 0.0, 0.0],
        top_k=10,
    )

    assert len(results) == 1
    assert results[0].chunk_id == "chunk-valid"


def test_vector_store_upsert_replaces_existing_record():

    store = FakeVectorStore()

    store.upsert(
        [
            VectorRecord(
                id="vector-1",
                vector=[1.0, 0.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-1",
                content="Original content",
            )
        ]
    )

    store.upsert(
        [
            VectorRecord(
                id="vector-1",
                vector=[0.0, 1.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-1",
                content="Updated content",
            )
        ]
    )

    results = store.search(
        tenant_id="tenant-a",
        query_vector=[0.0, 1.0, 0.0],
        top_k=10,
    )

    assert len(results) == 1
    assert results[0].content == "Updated content"
    assert results[0].score == 1.0

def test_vector_store_filters_by_metadata():
    store = FakeVectorStore()

    store.upsert(
        [
            VectorRecord(
                id="vector-finance",
                vector=[1.0, 0.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-finance",
                content="Finance document",
                metadata={
                    "department": "finance",
                },
            ),
            VectorRecord(
                id="vector-hr",
                vector=[1.0, 0.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-2",
                chunk_id="chunk-hr",
                content="HR document",
                metadata={
                    "department": "hr",
                },
            ),
        ]
    )

    results = store.search(
        tenant_id="tenant-a",
        query_vector=[1.0, 0.0, 0.0],
        top_k=10,
        filters={
            "department": "finance",
        },
    )

    assert len(results) == 1
    assert results[0].chunk_id == "chunk-finance"

def test_vector_store_filters_respect_tenant_boundary():
    store = FakeVectorStore()

    store.upsert(
        [
            VectorRecord(
                id="vector-a",
                vector=[1.0, 0.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-a",
                chunk_id="chunk-a",
                content="Tenant A finance",
                metadata={
                    "department": "finance",
                },
            ),
            VectorRecord(
                id="vector-b",
                vector=[1.0, 0.0, 0.0],
                tenant_id="tenant-b",
                document_id="document-b",
                chunk_id="chunk-b",
                content="Tenant B finance",
                metadata={
                    "department": "finance",
                },
            ),
        ]
    )

    results = store.search(
        tenant_id="tenant-a",
        query_vector=[1.0, 0.0, 0.0],
        top_k=10,
        filters={
            "department": "finance",
        },
    )

    assert len(results) == 1
    assert results[0].tenant_id == "tenant-a"
    assert results[0].chunk_id == "chunk-a"

def test_vector_store_returns_empty_for_unmatched_filter():
    store = FakeVectorStore()

    store.upsert(
        [
            VectorRecord(
                id="vector-1",
                vector=[1.0, 0.0, 0.0],
                tenant_id="tenant-a",
                document_id="document-1",
                chunk_id="chunk-1",
                content="Finance document",
                metadata={
                    "department": "finance",
                },
            )
        ]
    )

    results = store.search(
        tenant_id="tenant-a",
        query_vector=[1.0, 0.0, 0.0],
        top_k=10,
        filters={
            "department": "legal",
        },
    )

    assert results == []