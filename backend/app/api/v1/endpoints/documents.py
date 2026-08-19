# """
# Document processing endpoints.
# """

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from app.core.database import get_db
# from app.models.document import Document
# from app.schemas.document import DocumentProcessResponse
# from app.services.chunking.structural import StructuralChunker
# from app.services.ingestion import DocumentIngestionService
# from app.services.parsing.router import ParserRouter
# from app.services.storage.minio import storage


# router = APIRouter()


# parser_router = ParserRouter()
# chunker = StructuralChunker()

# ingestion_service = DocumentIngestionService(
#     storage=storage,
#     parser_router=parser_router,
#     chunker=chunker,
# )


# @router.post(
#     "/documents/{file_id}/process",
#     response_model=DocumentProcessResponse,
# )
# def process_document(
#     file_id: str,
#     db: Session = Depends(get_db),
# ):
#     document = (
#         db.query(Document)
#         .filter(Document.id == file_id)
#         .first()
#     )

#     if document is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Document not found.",
#         )

#     try:
#         parsed_document, chunks = (
#             ingestion_service.process_document(
#                 document=document,
#             )
#         )

#     except ValueError as exc:
#         raise HTTPException(
#             status_code=415,
#             detail=str(exc),
#         ) from exc

#     except Exception:
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to process document.",
#         )

#     return DocumentProcessResponse(
#         file_id=document.id,
#         filename=document.filename,
#         content_type=document.content_type,
#         status="processed",
#         page_count=parsed_document.page_count,
#         character_count=parsed_document.character_count,
#         extracted_text_preview=parsed_document.text[:2000],
#     )

# """
# Document processing endpoints.
# """

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from app.core.database import get_db
# from app.models.document import Document
# from app.schemas.document import DocumentProcessResponse
# from app.services.ingestion import DocumentIngestionService
# from app.services.parsing.router import ParserRouter
# from app.services.storage.minio import storage
# from app.services.chunking.structural import StructuralChunker


# router = APIRouter()


# parser_router = ParserRouter()
# chunker = StructuralChunker()

# ingestion_service = DocumentIngestionService(
#     storage=storage,
#     parser_router=parser_router,
#     chunker=chunker,
# )


# @router.post(
#     "/documents/{file_id}/process",
#     response_model=DocumentProcessResponse,
# )
# def process_document(
#     file_id: str,
#     db: Session = Depends(get_db),
# ):
#     # ---------------------------------------------------------------
#     # 1. Find document metadata
#     # ---------------------------------------------------------------

#     document = (
#         db.query(Document)
#         .filter(Document.id == file_id)
#         .first()
#     )

#     if document is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Document not found.",
#         )

#     # ---------------------------------------------------------------
#     # 2. Mark document as processing
#     # ---------------------------------------------------------------

#     document.status = "processing"
#     db.commit()
#     db.refresh(document)

#     # ---------------------------------------------------------------
#     # 3. Retrieve from storage and parse
#     # ---------------------------------------------------------------

#     try:
#         parsed_document = ingestion_service.process_document(
#             document=document,
#         )

#     except ValueError as exc:
#         document.status = "failed"
#         db.commit()

#         raise HTTPException(
#             status_code=415,
#             detail=str(exc),
#         ) from exc

#     except Exception:
#         document.status = "failed"
#         db.commit()

#         raise HTTPException(
#             status_code=500,
#             detail="Failed to process document.",
#         )

#     # ---------------------------------------------------------------
#     # 4. Mark document as processed
#     # ---------------------------------------------------------------

#     document.status = "processed"
#     db.commit()
#     db.refresh(document)

#     # ---------------------------------------------------------------
#     # 5. Return normalized extraction result
#     # ---------------------------------------------------------------

#     return DocumentProcessResponse(
#         file_id=document.id,
#         filename=document.filename,
#         content_type=document.content_type,
#         status=document.status,
#         page_count=parsed_document.page_count,
#         character_count=parsed_document.character_count,
#         extracted_text_preview=parsed_document.text[:2000],
#     )


"""
Document processing endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.repositories.chunk import ChunkRepository
from app.schemas.document import DocumentProcessResponse

from app.services.chunking.structural import StructuralChunker
from app.services.ingestion import DocumentIngestionService
from app.services.parsing.router import ParserRouter
from app.services.storage.minio import storage
from app.services.pii.noop import NoOpPIIProvider
from app.services.pii.service import PIIProcessingService

router = APIRouter()

parser_router = ParserRouter()
chunker = StructuralChunker()


@router.post(
    "/documents/{file_id}/process",
    response_model=DocumentProcessResponse,
)
def process_document(
    file_id: str,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == file_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    chunk_repository = ChunkRepository(db)

    pii_service = PIIProcessingService(
        provider=NoOpPIIProvider()
    )

    ingestion_service = DocumentIngestionService(
        storage=storage,
        parser_router=parser_router,
        chunker=chunker,
        pii_service=pii_service,
        chunk_repository=chunk_repository,
    )

    try:
        result = ingestion_service.process_document(
            document=document,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=415,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    normalized_document = result.document

    return DocumentProcessResponse(
        file_id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        status="processed",
        page_count=normalized_document.page_count,
        character_count=normalized_document.character_count,
        extracted_text_preview=normalized_document.text[:2000],
    )