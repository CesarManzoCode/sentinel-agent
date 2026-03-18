from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

from sentinel.domain.llm.ports import LLMPort
from sentinel.domain.llm.value_objects import PromptEnvelope, TokenUsage


@dataclass(slots=True)
class LLMGateway:
    provider: LLMPort
    renderer: Any  # 👈 AÑADIR ESTO
    retries: int = 2

    async def complete(self, prompt: PromptEnvelope) -> tuple[str, TokenUsage]:
        last_error: Exception | None = None

        for attempt in range(self.retries + 1):
            try:
                text, usage = await self.provider.complete(prompt)

                # 👇 DEBUG
                self.renderer.render_debug("LLM RAW OUTPUT", text)

                return text, usage

            except Exception as exc:  # pragma: no cover
                last_error = exc
                if attempt >= self.retries:
                    raise
                await asyncio.sleep(0.25 * (attempt + 1))

        assert last_error is not None
        raise last_error

    async def complete_json(self, prompt: str, schema: dict):
        text, usage = await self.complete(prompt)

        # 1. intento directo
        try:
            return json.loads(text), usage
        except Exception:
            pass

        # 2. intentar extraer JSON
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end]), usage
        except Exception:
            pass

        # 3. fallback
        return {
            "action": "respond",
            "response": text.strip() if text else "No response"
        }, usage