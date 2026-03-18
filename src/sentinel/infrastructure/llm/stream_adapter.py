from __future__ import annotations

import json
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass(slots=True)
class LLMStreamAdapter:
    async def iter_text(self, lines: AsyncIterator[str]) -> AsyncIterator[str]:
        async for line in lines:
            stripped = line.strip()
            if not stripped or stripped == "data: [DONE]":
                continue
            if stripped.startswith("data: "):
                stripped = stripped[6:]
            payload = json.loads(stripped)
            choices = payload.get("choices", [])
            if not choices:
                continue
            delta = choices[0].get("delta", {})
            if isinstance(delta, dict) and "content" in delta:
                yield str(delta["content"])
