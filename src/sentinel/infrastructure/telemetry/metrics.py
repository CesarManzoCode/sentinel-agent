from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass(slots=True)
class MetricsRecorder:
    counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    timings_ms: dict[str, list[int]] = field(default_factory=lambda: defaultdict(list))

    def increment(self, metric: str, amount: int = 1) -> None:
        self.counters[metric] = self.counters.get(metric, 0) + amount

    def observe(self, metric: str, value_ms: int) -> None:
        self.timings_ms.setdefault(metric, []).append(value_ms)

    def snapshot(self) -> dict[str, object]:
        return {
            "counters": dict(self.counters),
            "timings_ms": {key: values[-50:] for key, values in self.timings_ms.items()},
        }
