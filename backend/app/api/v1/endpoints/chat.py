"""
Chat endpoint.

For now this is a thin passthrough to BaseLLMProvider — it is the "LLM
input part" the frontend chat box talks to. Once the ingestion pipeline
and vector store exist, this is also where retrieval will be spliced in
(look up relevant chunks for the tenant, prepend them as context, then
call the same llm_provider — the chat box itself won't need to change).
"""
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.llm.litellm_provider import llm_provider

router = APIRouter()


async def _sse_event_stream(request: ChatRequest):
    """Stream LLM tokens as JSON-encoded Server-Sent Events."""

    async for token in llm_provider.stream_chat(
        request.messages,
        model=request.model,
    ):
        payload = {
            "type": "token",
            "content": token,
        }

        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    yield "data: [DONE]\n\n"


@router.post("/chat")
async def chat(request: ChatRequest):
    if request.stream:
        return StreamingResponse(
            _sse_event_stream(request),
            media_type="text/event-stream",
        )

    content = await llm_provider.chat(request.messages, model=request.model)
    return ChatResponse(message=ChatMessage(role="assistant", content=content))
