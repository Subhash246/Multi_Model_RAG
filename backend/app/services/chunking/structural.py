"""
Structural chunking implementation.

This initial implementation operates on page boundaries.

A future layout-aware implementation can consume Markdown
sections and produce richer parent-child structures without
changing the BaseChunker contract.
"""

from uuid import uuid4

from app.services.chunking.base import BaseChunker
from app.services.chunking.models import DocumentChunk
from app.services.parsing.models import NormalizedDocument


class StructuralChunker(BaseChunker):

    def chunk(
        self,
        document: NormalizedDocument,
    ) -> list[DocumentChunk]:

        chunks: list[DocumentChunk] = []

        for page in document.pages:

            if not page.text.strip():
                continue

            chunk = DocumentChunk(
                chunk_id=str(uuid4()),
                document_id=document.document_id,
                content=page.text.strip(),
                chunk_type="page",
                page_start=page.page_number,
                page_end=page.page_number,
                metadata={
                    "source": "parser",
                    "page_number": page.page_number,
                },
            )

            chunks.append(chunk)

        return chunks