"""
LiteLLMProvider — talks to the LiteLLM proxy, which in turn routes to
vLLM (self-hosted open-weight models) or any other configured provider.

Why go through LiteLLM instead of hitting vLLM directly?
- vLLM already exposes an OpenAI-compatible server, so LiteLLM isn't
  strictly required for a single local model.
- LiteLLM earns its place once you want routing/fallback (e.g. send 90%
  of traffic to a local Llama/Qwen model on vLLM, fall back to a hosted
  model for a subset of requests) without changing any application code —
  you only edit `litellm_config.yaml`.

We use the `openai` SDK to talk to LiteLLM because LiteLLM's proxy speaks
the OpenAI API schema natively.
"""
from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.schemas.chat import ChatMessage
from app.services.llm.base import BaseLLMProvider

settings = get_settings()


class LiteLLMProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            base_url=f"{settings.litellm_base_url}/v1",
            api_key=settings.litellm_api_key,
            timeout=settings.request_timeout_seconds,
        )

    def _to_openai_messages(self, messages: list[ChatMessage]) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=model or settings.default_model,
            messages=self._to_openai_messages(messages),
            stream=True,
            # Ensure model respects structured formatting and spacing instruction tokens
            temperature=0.3, 
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                # Yield the exact delta chunk
                yield delta

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
    ) -> str:
        response = await self._client.chat.completions.create(
            model=model or settings.default_model,
            messages=self._to_openai_messages(messages),
            stream=False,
        )
        return response.choices[0].message.content or ""


# A single shared instance. Swapping providers app-wide is a one-line
# change here (e.g. `llm_provider = OpenAIProvider()`), never in the
# endpoints that consume it.
llm_provider = LiteLLMProvider()
