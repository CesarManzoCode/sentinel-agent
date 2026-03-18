from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ToolModel:
    name: str
    description: str
    category: str
    schema_json: str
    baseline_risk: str
    timeout_seconds: int
    concurrency_safe: int
    side_effects_json: str
    enabled: int
    hidden: int
