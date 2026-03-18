from __future__ import annotations

import json
from dataclasses import dataclass

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolSpec
from sentinel.domain.tools.ports import ToolCatalogPort
from sentinel.domain.tools.value_objects import SideEffectProfile
from sentinel.infrastructure.persistence.db import DatabaseManager


@dataclass(slots=True)
class SQLiteToolCatalogRepository(ToolCatalogPort):
    db: DatabaseManager

    def save_tool(self, spec: ToolSpec) -> None:
        side_effects = spec.side_effects

        # -------- NORMALIZACIÓN --------

        # caso tuple accidental
        if isinstance(side_effects, tuple):
            side_effects = side_effects[0]

        # caso string (fallback legacy)
        if isinstance(side_effects, str):
            side_effects = {
                "level": side_effects,
                "requires_approval": False,
                "touches_filesystem": False,
                "touches_network": False,
            }

        # caso objeto correcto
        elif hasattr(side_effects, "level"):
            side_effects = {
                "level": side_effects.level,
                "requires_approval": side_effects.requires_approval,
                "touches_filesystem": side_effects.touches_filesystem,
                "touches_network": side_effects.touches_network,
            }

        # fallback extremo
        else:
            side_effects = {
                "level": "unknown",
                "requires_approval": False,
                "touches_filesystem": False,
                "touches_network": False,
            }

        side_effects_json = json.dumps(side_effects, ensure_ascii=False)

        with self.db.connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tool_catalog (
                    name, description, category, schema_json, baseline_risk, timeout_seconds,
                    concurrency_safe, side_effects_json, enabled, hidden
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    spec.name,
                    spec.description,
                    spec.category.value,
                    json.dumps(spec.schema, ensure_ascii=False),
                    spec.baseline_risk.value,
                    spec.timeout_seconds,
                    int(spec.concurrency_safe),
                    side_effects_json,
                    int(spec.enabled),
                    int(spec.hidden),
                ),
            )

    def list_enabled(self) -> list[ToolSpec]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tool_catalog WHERE enabled = 1 ORDER BY name ASC"
            ).fetchall()

        tools: list[ToolSpec] = []

        for row in rows:
            # -------- reconstruir SideEffectProfile --------
            side_effects_data = json.loads(row["side_effects_json"])

            side_effects = SideEffectProfile(
                side_effects_data["level"],
                side_effects_data["requires_approval"],
                side_effects_data["touches_filesystem"],
                side_effects_data["touches_network"],
            )

            tools.append(
                ToolSpec(
                    name=row["name"],
                    description=row["description"],
                    category=ToolCategory(row["category"]),
                    schema=json.loads(row["schema_json"]),
                    baseline_risk=RiskLevel(row["baseline_risk"]),
                    timeout_seconds=int(row["timeout_seconds"]),
                    concurrency_safe=bool(row["concurrency_safe"]),
                    side_effects=side_effects,
                    enabled=bool(row["enabled"]),
                    hidden=bool(row["hidden"]),
                )
            )

        return tools