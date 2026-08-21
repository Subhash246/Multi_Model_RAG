"""
Document processing endpoints.

API endpoints are responsible for HTTP concerns only.

Application and infrastructure dependencies are composed
outside the endpoint logic.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_ingestion_service
from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentProcessResponse
from app.services.ingestion import DocumentIngestionService
from app.services.security.context import SecurityContext
from app.services.security.dependency import get_security_context


router = APIRouter()


# -------------------------------------------------------------------
# Document processing endpoint
# -------------------------------------------------------------------

@router.post(
    "/documents/{file_id}/process",
    response_model=DocumentProcessResponse,
)
def process_document(
    file_id: str,
    db: Session = Depends(get_db),
    security_context: SecurityContext = Depends(
        get_security_context
    ),
    ingestion_service: DocumentIngestionService = Depends(
        get_ingestion_service
    ),
):
    # ---------------------------------------------------------------
    # 1. Find document within the current tenant
    # ---------------------------------------------------------------

    document = (
        db.query(Document)
        .filter(
            Document.id == file_id,
            Document.tenant_id == security_context.tenant_id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # ---------------------------------------------------------------
    # 2. Prevent invalid processing states
    # ---------------------------------------------------------------

    if document.status == "processing":
        raise HTTPException(
            status_code=409,
            detail="Document is already being processed.",
        )

    if document.status == "processed":
        raise HTTPException(
            status_code=409,
            detail="Document has already been processed.",
        )

    # ---------------------------------------------------------------
    # 3. Mark document as processing
    # ---------------------------------------------------------------

    document.status = "processing"
    db.commit()
    db.refresh(document)

    # ---------------------------------------------------------------
    # 4. Execute ingestion pipeline
    # ---------------------------------------------------------------

    try:
        result = ingestion_service.process_document(
            document=document,
            security_context=security_context,
        )

    except PermissionError as exc:
        db.rollback()

        document.status = "failed"
        db.commit()

        raise HTTPException(
            status_code=403,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        db.rollback()

        document.status = "failed"
        db.commit()

        raise HTTPException(
            status_code=415,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        document.status = "failed"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail="Failed to process document.",
        ) from exc

    # ---------------------------------------------------------------
    # 5. Mark document as processed
    # ---------------------------------------------------------------

    document.status = "processed"
    db.commit()
    db.refresh(document)

    # ---------------------------------------------------------------
    # 6. Return processing result
    # ---------------------------------------------------------------

    normalized_document = result.document

    return DocumentProcessResponse(
        file_id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        status=document.status,
        page_count=normalized_document.page_count,
        character_count=normalized_document.character_count,
        extracted_text_preview=normalized_document.text[:2000],
    )