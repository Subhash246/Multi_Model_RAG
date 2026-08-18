from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class Attachment(BaseModel):
    """Metadata for a file that was uploaded alongside a chat turn.

    The actual file bytes go through /api/v1/upload first; the chat
    request only references the resulting id. This keeps the chat
    payload small and lets the ingestion pipeline (Docling/Whisper/etc,
    per the architecture doc) process files independently of the chat
    request/response cycle.
    """

    file_id: str
    filename: str
    content_type: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = Field(default=None, description="Overrides the default model configured in LiteLLM")
    attachments: list[Attachment] = Field(default_factory=list)
    stream: bool = True


class ChatResponse(BaseModel):
    message: ChatMessage
