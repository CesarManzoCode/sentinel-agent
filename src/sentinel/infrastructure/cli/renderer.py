from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any

try:  # pragma: no cover
    from rich.console import Console
    from rich.panel import Panel
except Exception:  # pragma: no cover
    Console = None
    Panel = None


@dataclass(slots=True)
class TerminalRenderer:
    use_rich: bool = True
    debug_mode: bool = False  # 👈 NUEVO
    _console: Optional[Any] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        if self.use_rich:
            try:
                self._console = Console()
            except Exception:
                self._console = None
        else:
            self._console = None

    def info(self, message: str) -> None:
        if self._console:
            self._console.print(message)
        else:
            print(message)

    def assistant(self, message: str) -> None:
        if self._console and Panel is not None:
            self._console.print(Panel(message, title="assistant"))
        else:
            print(f"assistant> {message}")

    def status(self, message: str) -> None:
        if self._console:
            self._console.print(f"[cyan]{message}[/cyan]")
        else:
            print(f"[status] {message}")

    def error(self, message: str) -> None:
        if self._console:
            self._console.print(f"[red]{message}[/red]")
        else:
            print(f"error: {message}")

    # 👇 DEBUG MODE
    def render_debug(self, title: str, content: str):
        if not self.debug_mode:
            return

        if self._console:
            self._console.print(f"\n[bold yellow]===== {title} =====[/bold yellow]")
            self._console.print(content)
            self._console.print("[bold yellow]==========================[/bold yellow]\n")
        else:
            print(f"\n===== {title} =====")
            print(content)
            print("==========================\n")