from __future__ import annotations

from dataclasses import dataclass

from sentinel.infrastructure.cli.renderer import TerminalRenderer


@dataclass(slots=True)
class StreamingRenderer:
    renderer: TerminalRenderer

    def stream_text(self, text: str) -> None:
        self.renderer.assistant(text)

    def stream_status(self, event: str) -> None:
        self.renderer.status(event)
