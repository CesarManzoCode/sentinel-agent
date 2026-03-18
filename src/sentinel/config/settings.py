from __future__ import annotations
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

import os
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from sentinel.config.paths import PathResolver
from sentinel.config.profiles import ExecutionProfile, PROFILES
from sentinel.shared.constants import (
    DEFAULT_APPROVAL_TTL_SECONDS,
    DEFAULT_EMBEDDING_DIM,
    DEFAULT_MAX_STEPS_PER_TURN,
    DEFAULT_MAX_TOOL_CALLS_PER_TURN,
    DEFAULT_MEMORY_TOP_K,
)


@dataclass(slots=True)
class LLMSettings:
    provider: str = "groq"
    model: str = "llama-3.3-70b-versatile"
    base_url: str = "https://api.groq.com/openai/v1"
    api_key: str = ""
    temperature: float = 0.1
    timeout_seconds: int = 60
    stream: bool = True


@dataclass(slots=True)
class MemorySettings:
    top_k: int = DEFAULT_MEMORY_TOP_K
    embedding_dim: int = DEFAULT_EMBEDDING_DIM
    consolidation_enabled: bool = True


@dataclass(slots=True)
class SafetySettings:
    allow_privileged: bool = False
    enable_bwrap: bool = True
    approval_ttl_seconds: int = DEFAULT_APPROVAL_TTL_SECONDS
    workspace_roots: list[str] = field(default_factory=lambda: ["~/work", "~/projects", "~/src"])
    denied_binaries: list[str] = field(
        default_factory=lambda: ["sudo", "su", "doas", "pkexec", "rm", "dd", "mkfs", "shutdown", "reboot"]
    )


@dataclass(slots=True)
class TelemetrySettings:
    trace_persist: bool = True
    metrics_enabled: bool = True
    json_logs: bool = False


@dataclass(slots=True)
class CLISettings:
    streaming: bool = True
    verbose: bool = False
    multiline: bool = False


@dataclass(slots=True)
class AppSettings:
    env: str = "development"
    profile_name: str = "balanced"
    debug: bool = False
    log_level: str = "INFO"
    data_dir: Path = Path("data")
    config_file: Path | None = None
    max_steps_per_turn: int = DEFAULT_MAX_STEPS_PER_TURN
    max_tool_calls_per_turn: int = DEFAULT_MAX_TOOL_CALLS_PER_TURN


@dataclass(slots=True)
class Settings:
    app: AppSettings = field(default_factory=AppSettings)
    llm: LLMSettings = field(default_factory=LLMSettings)
    memory: MemorySettings = field(default_factory=MemorySettings)
    safety: SafetySettings = field(default_factory=SafetySettings)
    telemetry: TelemetrySettings = field(default_factory=TelemetrySettings)
    cli: CLISettings = field(default_factory=CLISettings)

    @property
    def profile(self) -> ExecutionProfile:
        return PROFILES.get(self.app.profile_name, PROFILES["balanced"])

    @property
    def paths(self) -> PathResolver:
        return PathResolver(self.app.data_dir)

    def ensure_directories(self) -> None:
        self.paths.ensure()

    @classmethod
    def load(cls, config_file: Path | None = None) -> "Settings":
        config = cls()
        env_config_path = os.getenv("SENTINEL_CONFIG_FILE")
        if config_file is None and env_config_path:
            config_file = Path(env_config_path)
        if config_file is not None and config_file.exists():
            cls._apply_file(config, config_file)
            config.app.config_file = config_file
        cls._apply_env(config)
        config.app.data_dir = Path(os.path.expanduser(str(config.app.data_dir))).resolve()
        config.ensure_directories()
        return config

    @staticmethod
    def _apply_file(settings: "Settings", config_file: Path) -> None:
        payload = tomllib.loads(config_file.read_text(encoding="utf-8"))
        for section_name, values in payload.items():
            section = getattr(settings, section_name, None)
            if section is None or not isinstance(values, dict):
                continue
            for key, value in values.items():
                if hasattr(section, key):
                    setattr(section, key, value)

    @staticmethod
    def _bool(name: str, default: bool) -> bool:
        raw = os.getenv(name)
        if raw is None:
            return default
        return raw.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _apply_env(settings: "Settings") -> None:
        settings.app.env = os.getenv("SENTINEL_ENV", settings.app.env)
        settings.app.profile_name = os.getenv("SENTINEL_PROFILE", settings.app.profile_name)
        settings.app.log_level = os.getenv("SENTINEL_LOG_LEVEL", settings.app.log_level)
        settings.app.debug = Settings._bool("SENTINEL_DEBUG", settings.app.debug)
        settings.app.data_dir = Path(os.getenv("SENTINEL_DATA_DIR", str(settings.app.data_dir)))

        settings.llm.api_key = os.getenv("SENTINEL_GROQ_API_KEY", settings.llm.api_key)
        settings.llm.model = os.getenv("SENTINEL_GROQ_MODEL", settings.llm.model)
        settings.llm.base_url = os.getenv("SENTINEL_GROQ_BASE_URL", settings.llm.base_url)

        settings.memory.top_k = int(os.getenv("SENTINEL_MEMORY_TOP_K", str(settings.memory.top_k)))
        settings.memory.embedding_dim = int(
            os.getenv("SENTINEL_MEMORY_EMBEDDING_DIM", str(settings.memory.embedding_dim))
        )
        settings.memory.consolidation_enabled = Settings._bool(
            "SENTINEL_MEMORY_CONSOLIDATION_ENABLED",
            settings.memory.consolidation_enabled,
        )

        settings.safety.allow_privileged = Settings._bool(
            "SENTINEL_ALLOW_PRIVILEGED", settings.safety.allow_privileged
        )
        settings.safety.enable_bwrap = Settings._bool(
            "SENTINEL_ENABLE_BWRAP", settings.safety.enable_bwrap
        )
        settings.safety.approval_ttl_seconds = int(
            os.getenv("SENTINEL_APPROVAL_TTL_SECONDS", str(settings.safety.approval_ttl_seconds))
        )
        roots = os.getenv("SENTINEL_WORKSPACE_ROOTS")
        if roots:
            settings.safety.workspace_roots = [root.strip() for root in roots.split(",") if root.strip()]

        settings.telemetry.trace_persist = Settings._bool(
            "SENTINEL_TRACE_PERSIST", settings.telemetry.trace_persist
        )
        settings.telemetry.metrics_enabled = Settings._bool(
            "SENTINEL_METRICS_ENABLED", settings.telemetry.metrics_enabled
        )
        settings.telemetry.json_logs = os.getenv("SENTINEL_LOG_FORMAT", "human").lower() == "json"

        settings.cli.streaming = Settings._bool("SENTINEL_CLI_STREAMING", settings.cli.streaming)
        settings.cli.verbose = Settings._bool("SENTINEL_CLI_VERBOSE", settings.cli.verbose)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
