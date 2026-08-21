from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.services.chunking.models import DocumentChunk


class ChunkRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_many(
        self,
        chunks: list[DocumentChunk],
    ) -> list[Chunk]:

        db_chunks: list[Chunk] = []

        for chunk in chunks:
            db_chunk = Chunk(
                id=chunk.chunk_id,
                document_id=chunk.document_id,
                tenant_id=chunk.tenant_id,
                content=chunk.content,

                access_tags=chunk.access_tags,

                chunk_type=chunk.chunk_type,
                parent_id=chunk.parent_id,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                chunk_metadata=chunk.metadata,
            )

            self.db.add(db_chunk)
            db_chunks.append(db_chunk)

        self.db.commit()

        return db_chunks