"""
Application dependency wiring.

This module composes concrete infrastructure providers
into application services.

API endpoints should depend on application services,
not construct infrastructure implementations directly.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.chunk import ChunkRepository
from app.services.chunking.structural import StructuralChunker
from app.services.embedding.fake import FakeEmbeddingProvider
from app.services.indexing import IndexingService
from app.services.ingestion import DocumentIngestionService
from app.services.parsing.router import ParserRouter
from app.services.pii.noop import NoOpPIIProvider
from app.services.pii.service import PIIProcessingService
from app.services.storage.minio import storage
from app.services.vector.fake import FakeVectorStore


# ------------------------------------------------------------------
# Shared stateless infrastructure
# ------------------------------------------------------------------

parser_router = ParserRouter()

chunker = StructuralChunker()

embedding_provider = FakeEmbeddingProvider()

vector_store = FakeVectorStore()

indexing_service = IndexingService(
    embedding_provider=embedding_provider,
    vector_store=vector_store,
)


# ------------------------------------------------------------------
# Application service factory
# ------------------------------------------------------------------

def get_ingestion_service(
    db: Session = Depends(get_db),
) -> DocumentIngestionService:
    """
    Build the document ingestion service with its
    application dependencies.

    FastAPI provides the database session through
    get_db().
    """

    chunk_repository = ChunkRepository(db)

    pii_service = PIIProcessingService(
        provider=NoOpPIIProvider()
    )

    return DocumentIngestionService(
        storage=storage,
        parser_router=parser_router,
        chunker=chunker,
        pii_service=pii_service,
        chunk_repository=chunk_repository,
        indexing_service=indexing_service,
    )