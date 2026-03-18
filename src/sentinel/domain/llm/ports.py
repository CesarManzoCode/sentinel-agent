from __future__ import annotations

from typing import AsyncIterator, Protocol

from sentinel.domain.llm.value_objects import PromptEnvelope, TokenUsage


class LLMPort(Protocol):
    async def complete(self, prompt: PromptEnvelope) -> tuple[str, TokenUsage]: ...
    async def complete_json(self, prompt: PromptEnvelope, schema: dict[str, object]) -> tuple[dict[str, object], TokenUsage]: ...
    async def stream(self, prompt: PromptEnvelope) -> AsyncIterator[str]: ...
