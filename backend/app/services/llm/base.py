"""
BaseLLMProvider — the abstract interface every LLM backend must satisfy.

This mirrors the "6 abstract interfaces" pattern from the architecture
docs: the rest of the app (chat endpoint, RAG pipeline, agents) only ever
depends on this interface. Today the adapter is LiteLLM sitting in front
of a vLLM server. Later you could add a second adapter (e.g. a direct
OpenAI adapter for fallback) without touching any calling code.
"""
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.schemas.chat import ChatMessage


class BaseLLMProvider(ABC):
    @abstractmethod
    async def stream_chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        """Yield response text chunks as they arrive from the model."""
        raise NotImplementedError

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
    ) -> str:
        """Return the full, non-streamed response text."""
        raise NotImplementedError
