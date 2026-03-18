from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.llm.value_objects import TokenUsage


@dataclass(slots=True)
class ProviderResponseParser:
    def parse_text(self, payload: dict[str, object]) -> tuple[str, TokenUsage]:
        choices = payload.get("choices", [])
        if not isinstance(choices, list) or not choices:
            return "", TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        first = choices[0]
        assert isinstance(first, dict)
        message = first.get("message", {})
        assert isinstance(message, dict)
        content = str(message.get("content", ""))
        usage_raw = payload.get("usage", {})
        assert isinstance(usage_raw, dict)
        usage = TokenUsage(
            prompt_tokens=int(usage_raw.get("prompt_tokens", 0)),
            completion_tokens=int(usage_raw.get("completion_tokens", 0)),
            total_tokens=int(usage_raw.get("total_tokens", 0)),
        )
        return content, usage
