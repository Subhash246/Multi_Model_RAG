"""
Document ingestion service.

Coordinates retrieval, parsing, chunking, PII processing,
and persistence.

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


class DocumentIngestionService:

    def __init__(
        self,
        storage: BaseStorageProvider,
        parser_router: ParserRouter,
        chunker: BaseChunker,
        pii_service: PIIProcessingService,
        chunk_repository: ChunkRepository,
    ) -> None:

        self.storage = storage
        self.parser_router = parser_router
        self.chunker = chunker
        self.pii_service = pii_service
        self.chunk_repository = chunk_repository

    def process_document(
        self,
        document: Document,
    ) -> ChunkedDocument:
        """
        Download a document from object storage,
        parse it, chunk it, process PII,
        and persist the chunks.
        """

        # ---------------------------------------------------------
        # 1. Retrieve raw file
        # ---------------------------------------------------------

        file_data = self.storage.download(
            document.storage_key
        )

        # ---------------------------------------------------------
        # 2. Select parser
        # ---------------------------------------------------------

        parser = self.parser_router.get_parser(
            document.content_type
        )

        # ---------------------------------------------------------
        # 3. Parse document
        # ---------------------------------------------------------

        normalized_document = parser.parse(
            file_data=file_data,
            content_type=document.content_type,
            document_id=document.id,
        )

        # ---------------------------------------------------------
        # 4. Chunk document
        # ---------------------------------------------------------

        chunks = self.chunker.chunk(
            normalized_document
        )

        # ---------------------------------------------------------
        # 5. Process PII
        # ---------------------------------------------------------

        processed_chunks = []

        for chunk in chunks:
            processed_chunk = self.pii_service.process_chunk(
                chunk
            )

            processed_chunks.append(processed_chunk)

        # ---------------------------------------------------------
        # 6. Persist processed chunks
        # ---------------------------------------------------------

        self.chunk_repository.create_many(
            processed_chunks
        )

        # ---------------------------------------------------------
        # 7. Return complete ingestion result
        # ---------------------------------------------------------

        return ChunkedDocument(
            document=normalized_document,
            chunks=processed_chunks,
        )