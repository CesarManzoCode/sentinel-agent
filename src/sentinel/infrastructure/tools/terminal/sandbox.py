from __future__ import annotations

import os
import resource
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CommandSandbox:
    allow_bwrap: bool
    env_allowlist: set[str]
    workspace_roots: list[Path]

    def prepare(
        self,
        executable: str,
        argv: list[str],
        cwd: str | None,
        env_overrides: dict[str, str],
    ) -> tuple[list[str], str | None, dict[str, str], str]:
        base_env = {key: value for key, value in os.environ.items() if key in self.env_allowlist}
        base_env.update(env_overrides)
        boundary = "process"
        final_argv = [executable, *argv]
        if self.allow_bwrap and shutil.which("bwrap") and cwd:
            boundary = "bubblewrap"
            final_argv = [
                "bwrap",
                "--ro-bind",
                "/",
                "/",
                "--proc",
                "/proc",
                "--dev",
                "/dev",
                "--chdir",
                cwd,
                executable,
                *argv,
            ]
        return final_argv, cwd, base_env, boundary

    @staticmethod
    def preexec() -> None:
        try:
            os.setsid()
            resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
            resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        except Exception:
            return
