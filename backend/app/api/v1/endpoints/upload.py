import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.storage.minio import storage


router = APIRouter()

settings = get_settings()


ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "image/png",
    "image/jpeg",
    "audio/mpeg",
    "audio/wav",
    "audio/webm",
    "video/mp4",
}


@router.post(
    "/upload",
    response_model=DocumentResponse,
)
async def upload_file(
    file: UploadFile,
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    content_type = (
        file.content_type
        or "application/octet-stream"
    )

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {content_type}",
        )

    file_id = str(uuid.uuid4())

    storage_key = (
        f"{file_id}/{file.filename}"
    )

    file_data = await file.read()

    size_bytes = len(file_data)

    max_size_bytes = (
        settings.max_upload_mb
        * 1024
        * 1024
    )

    if size_bytes > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File exceeds the maximum "
                f"size of {settings.max_upload_mb} MB."
            ),
        )

    try:
        from io import BytesIO

        storage.upload(
            file_data=BytesIO(file_data),
            object_name=storage_key,
            content_type=content_type,
            size=size_bytes,
        )

        document = Document(
            id=file_id,
            filename=file.filename,
            content_type=content_type,
            size_bytes=size_bytes,
            storage_key=storage_key,
            status="uploaded",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return DocumentResponse(
            file_id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            status=document.status,
            created_at=document.created_at,
        )

    except Exception as exc:
        db.rollback()

        try:
            storage.delete(storage_key)
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="Failed to store uploaded file.",
        ) from exc