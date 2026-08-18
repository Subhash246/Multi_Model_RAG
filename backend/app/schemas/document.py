from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    file_id: str
    filename: str
    content_type: str
    size_bytes: int
    status: str
    created_at: datetime