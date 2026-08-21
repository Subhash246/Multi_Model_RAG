"""
Document ingestion service.

Coordinates raw document retrieval from object storage,
parsing, chunking, PII processing, and persistence.

This service does not know about MinIO or specific
parsing libraries or PII implementations.
"""

from app.models.document import Document
from app.repositories.chunk import ChunkRepository
from app.services.chunking.base import BaseChunker
from app.services.chunking.models import ChunkedDocument
from app.services.parsing.router import ParserRouter
from app.services.pii.service import PIIProcessingService
from app.services.storage.base import BaseStorageProvider
from app.services.security.context import SecurityContext
from app.services.security.policy import SecurityPolicy
from app.services.indexing import IndexingService

class DocumentIngestionService:

    def __init__(
        self,
        storage: BaseStorageProvider,
        parser_router: ParserRouter,
        chunker: BaseChunker,
        pii_service: PIIProcessingService,
        chunk_repository: ChunkRepository,
        indexing_service: IndexingService,
    ) -> None:

        self.storage = storage
        self.parser_router = parser_router
        self.chunker = chunker
        self.pii_service = pii_service
        self.chunk_repository = chunk_repository
        self.indexing_service = indexing_service

    def process_document(
        self,
        document: Document,
        security_context: SecurityContext,
    ) -> ChunkedDocument:

        # ---------------------------------------------------------------
        # 1. Authorization
        # ---------------------------------------------------------------
        if not SecurityPolicy.can_ingest_document(
            security_context,
            document.tenant_id,
        ):
            raise PermissionError(
                "You are not authorized to ingest this document."
            )

        # ---------------------------------------------------------------
        # 2. Retrieve document from object storage
        # ---------------------------------------------------------------
        file_data = self.storage.download(
            document.storage_key
        )

        # ---------------------------------------------------------------
        # 3. Select parser
        # ---------------------------------------------------------------
        parser = self.parser_router.get_parser(
            document.content_type
        )

        # ---------------------------------------------------------------
        # 4. Parse document
        # ---------------------------------------------------------------
        normalized_document = parser.parse(
            file_data=file_data,
            content_type=document.content_type,
            document_id=document.id,
        )

        # ---------------------------------------------------------------
        # 5. Attach security metadata
        # ---------------------------------------------------------------
        normalized_document.tenant_id = (
            security_context.tenant_id
        )

        # Do NOT automatically make every document public.
        # For now, inherit a controlled default access tag.
        normalized_document.access_tags = [
            f"tenant:{security_context.tenant_id}"
        ]

        # ---------------------------------------------------------------
        # 6. Chunk
        # ---------------------------------------------------------------
        chunks = self.chunker.chunk(
            normalized_document
        )

        # ---------------------------------------------------------------
        # 7. PII processing
        # ---------------------------------------------------------------
        processed_chunks = []

        for chunk in chunks:
            processed_chunk = (
                self.pii_service.process_chunk(chunk)
            )
            processed_chunks.append(processed_chunk)

        # ---------------------------------------------------------------
        # 8. Persist chunks
        # ---------------------------------------------------------------
        self.chunk_repository.create_many(
            processed_chunks
        )

        self.indexing_service.index_chunks(
            processed_chunks
        )

        # ---------------------------------------------------------------
        # 9. Return pipeline result
        # ---------------------------------------------------------------
        return ChunkedDocument(
            document=normalized_document,
            chunks=processed_chunks,
        )