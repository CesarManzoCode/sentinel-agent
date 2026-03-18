from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any


class Serializer:
    @staticmethod
    def to_json(value: Any) -> str:
        if is_dataclass(value):
            return json.dumps(asdict(value), ensure_ascii=False, sort_keys=True, default=str)
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)

    @staticmethod
    def from_json[T](payload: str) -> T:
        return json.loads(payload)
