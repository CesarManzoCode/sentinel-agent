from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.errors import StructuredOutputError


@dataclass(slots=True)
class StructuredOutputService:
    def validate_directive(self, payload: dict) -> dict:
        if not isinstance(payload, dict):
            return {"action": "respond", "response": str(payload)}

        action = payload.get("action")

        if not action:
            return {
                "action": "respond",
                "response": payload.get("response") or payload.get("content") or ""
            }

        return payload

    def validate_response(self, payload: dict[str, object], required_keys: set[str]) -> dict[str, object]:
        missing = required_keys.difference(payload)
        if missing:
            raise StructuredOutputError(f"missing keys in structured payload: {sorted(missing)}")
        return payload
