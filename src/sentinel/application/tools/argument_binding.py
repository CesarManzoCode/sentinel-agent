from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.errors import InvalidToolInvocation
from sentinel.domain.tools.entities import ToolSpec


@dataclass(slots=True)
class ArgumentBinder:
    def bind(self, spec: ToolSpec, arguments: dict[str, object]) -> dict[str, object]:
        schema_properties = spec.schema.get("properties", {})
        required = set(spec.schema.get("required", []))
        missing = [name for name in required if name not in arguments]
        if missing:
            raise InvalidToolInvocation(f"missing required arguments for {spec.name}: {missing}")
        bound: dict[str, object] = {}
        for name in schema_properties:
            if name in arguments:
                bound[name] = arguments[name]
        extra = set(arguments).difference(schema_properties)
        if extra:
            raise InvalidToolInvocation(f"unexpected arguments for {spec.name}: {sorted(extra)}")
        return bound
