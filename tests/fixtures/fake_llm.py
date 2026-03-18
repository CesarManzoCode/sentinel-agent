from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import AsyncIterator

from sentinel.domain.llm.ports import LLMPort
from sentinel.domain.llm.value_objects import PromptEnvelope, TokenUsage


@dataclass(slots=True)
class FakeLLM(LLMPort):
    plan_queue: list[dict[str, object]] = field(default_factory=list)
    response_queue: list[str] = field(default_factory=list)
    captured_prompts: list[PromptEnvelope] = field(default_factory=list)

    async def complete(self, prompt: PromptEnvelope) -> tuple[str, TokenUsage]:
        self.captured_prompts.append(prompt)
        response = self.response_queue.pop(0) if self.response_queue else "synthetic response"
        usage = TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        return response, usage

    async def complete_json(
        self, prompt: PromptEnvelope, schema: dict[str, object]
    ) -> tuple[dict[str, object], TokenUsage]:
        self.captured_prompts.append(prompt)
        if self.plan_queue:
            payload = self.plan_queue.pop(0)
        else:
            payload = {"action": "respond", "response": "synthetic response", "confidence": 0.9}
        usage = TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30)
        return payload, usage

    async def stream(self, prompt: PromptEnvelope) -> AsyncIterator[str]:
        self.captured_prompts.append(prompt)
        text = self.response_queue[0] if self.response_queue else "synthetic response"
        for token in text.split():
            yield token + " "
