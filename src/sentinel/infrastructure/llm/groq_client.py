from __future__ import annotations

import json
from dataclasses import dataclass
from typing import AsyncIterator

import httpx

from sentinel.domain.common.errors import StructuredOutputError
from sentinel.domain.llm.ports import LLMPort
from sentinel.domain.llm.value_objects import PromptEnvelope, TokenUsage
from sentinel.infrastructure.llm.response_parser import ProviderResponseParser
from sentinel.infrastructure.llm.stream_adapter import LLMStreamAdapter


@dataclass(slots=True)
class GroqLLMClient(LLMPort):
    api_key: str
    model: str
    base_url: str
    timeout_seconds: int
    parser: ProviderResponseParser
    stream_adapter: LLMStreamAdapter

    async def complete(self, prompt):
        payload = self._payload(prompt)

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        data = response.json()

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        return content, {}

    async def complete_json(
        self, prompt: PromptEnvelope, schema: dict[str, object]
    ) -> tuple[dict[str, object], TokenUsage]:
        payload = self._payload(prompt)
        payload["response_format"] = {"type": "json_object"}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            text, usage = self.parser.parse_text(response.json())
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise StructuredOutputError(f"provider did not return valid JSON: {text[:200]}") from exc
        return parsed, usage

    async def stream(self, prompt: PromptEnvelope) -> AsyncIterator[str]:
        payload = self._payload(prompt)
        payload["stream"] = True
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                async for token in self.stream_adapter.iter_text(response.aiter_lines()):
                    yield token

    def _payload(self, prompt):
        # -------- NORMALIZACIÓN --------

        if isinstance(prompt, str):
            return {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
            }

        # soporte futuro para PromptEnvelope
        if hasattr(prompt, "context"):
            content = "\n".join(
                f"{key}: {value}" for key, value in prompt.context.items()
            )
            return {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": content}
                ],
                "temperature": 0.2,
            }

        # fallback extremo
        return {
            "model": self.model,
            "messages": [
                {"role": "user", "content": str(prompt)}
            ],
            "temperature": 0.2,
        }

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
