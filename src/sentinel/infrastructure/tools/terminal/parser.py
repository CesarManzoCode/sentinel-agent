from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.errors import InvalidToolInvocation


@dataclass(slots=True)
class CommandParser:
    def parse(self, arguments: dict[str, object]) -> tuple[str, list[str], str | None, dict[str, str]]:
        executable = str(arguments.get("executable", "")).strip()
        if not executable:
            raise InvalidToolInvocation("terminal.exec requires a non-empty executable")
        raw_argv = arguments.get("argv", [])
        if raw_argv is None:
            raw_argv = []
        if not isinstance(raw_argv, list):
            raise InvalidToolInvocation("terminal.exec argv must be a list of strings")
        argv = [str(item) for item in raw_argv]
        cwd = str(arguments["cwd"]) if "cwd" in arguments and arguments["cwd"] is not None else None
        raw_env = arguments.get("env", {})
        if raw_env is None:
            raw_env = {}
        if not isinstance(raw_env, dict):
            raise InvalidToolInvocation("terminal.exec env must be an object")
        env = {str(key): str(value) for key, value in raw_env.items()}
        return executable, argv, cwd, env
