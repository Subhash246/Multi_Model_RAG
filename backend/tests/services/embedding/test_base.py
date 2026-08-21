from app.services.embedding.fake import FakeEmbeddingProvider


def test_embedding_provider():
    provider = FakeEmbeddingProvider()

    result = provider.embed_text(
        "hello world"
    )

    assert result.vector == [0.1, 0.2, 0.3]
    assert result.model == "fake-model"
    assert result.dimensions == 3


def test_embedding_provider_batch():
    provider = FakeEmbeddingProvider()

    results = provider.embed_documents(
        [
            "hello",
            "world",
        ]
    )

    assert len(results) == 2

    for result in results:
        assert result.vector == [0.1, 0.2, 0.3]
        assert result.model == "fake-model"
        assert result.dimensions == 3


def test_embedding_provider_query():
    provider = FakeEmbeddingProvider()

    result = provider.embed_query(
        "What is retrieval?"
    )

    assert result.vector == [0.1, 0.2, 0.3]
    assert result.model == "fake-model"
    assert result.dimensions == 3
    assert result.metadata["provider"] == "fake"