from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from sentinel.config.settings import Settings
from sentinel.shared.utils import ensure_directory


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, self.datefmt),
        }
        for field_name in ("session_id", "trace_id", "event", "tool_name"):
            value = getattr(record, field_name, None)
            if value is not None:
                payload[field_name] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


@dataclass(slots=True)
class LoggingConfigurator:
    settings: Settings

    def configure(self) -> None:
        logs_dir = ensure_directory(self.settings.paths.logs_dir)
        root = logging.getLogger()
        root.setLevel(getattr(logging, self.settings.app.log_level.upper(), logging.INFO))
        root.handlers.clear()

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._console_formatter())
        root.addHandler(console_handler)

        file_handler = RotatingFileHandler(
            filename=Path(logs_dir) / "app.log",
            maxBytes=5_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(JsonFormatter() if self.settings.telemetry.json_logs else self._console_formatter())
        root.addHandler(file_handler)

    @staticmethod
    def _console_formatter() -> logging.Formatter:
        return logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
