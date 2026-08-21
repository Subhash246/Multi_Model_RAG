"""
Indexing service.

Converts processed document chunks into embeddings and
provider-agnostic vector records.
"""

from app.services.chunking.models import DocumentChunk
from app.services.embedding.base import BaseEmbeddingProvider
from app.services.vector.base import BaseVectorStore
from app.services.vector.models import VectorRecord


class IndexingService:

    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: BaseVectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def index_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> None:

        if not chunks:
            return

        texts = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_provider.embed_documents(texts)
        )

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Embedding provider returned a different "
                "number of results than the input chunks."
            )

        records: list[VectorRecord] = []

        for chunk, embedding in zip(chunks, embeddings):

            records.append(
                VectorRecord(
                    id=chunk.chunk_id,
                    vector=embedding.vector,
                    tenant_id=chunk.tenant_id,
                    document_id=chunk.document_id,
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    metadata={
                        **chunk.metadata,
                        "chunk_type": chunk.chunk_type,
                        "parent_id": chunk.parent_id,
                        "page_start": chunk.page_start,
                        "page_end": chunk.page_end,
                        "access_tags": chunk.access_tags,
                        "embedding_model": embedding.model,
                        "embedding_dimensions": embedding.dimensions,
                    },
                )
            )

        self.vector_store.upsert(records)