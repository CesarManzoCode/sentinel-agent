from __future__ import annotations

import asyncio
from dataclasses import dataclass

from sentinel.infrastructure.cli.commands import CommandRouter
from sentinel.infrastructure.cli.prompts import PromptFactory
from sentinel.infrastructure.cli.renderer import TerminalRenderer
from sentinel.interfaces.cli.controllers import ApprovalController, ChatController, MemoryController, ToolController, TraceController
from sentinel.interfaces.cli.presenters import ApprovalPresenter, ChatPresenter, MemoryPresenter, ToolPresenter, TracePresenter


@dataclass(slots=True)
class ChatLoop:
    chat_controller: ChatController
    approval_controller: ApprovalController
    trace_controller: TraceController
    tool_controller: ToolController
    memory_controller: MemoryController
    renderer: TerminalRenderer
    prompts: PromptFactory
    router: CommandRouter
    chat_presenter: ChatPresenter
    approval_presenter: ApprovalPresenter
    trace_presenter: TracePresenter
    tool_presenter: ToolPresenter
    memory_presenter: MemoryPresenter

    async def run(self) -> int:
        session_id: str | None = None
        debug = False
        self.renderer.info("Sentinel interactive chat. Type /help for commands.")
        while True:
            try:
                raw = self.prompts.read().strip()
            except EOFError:
                self.renderer.info("")
                return 0
            if not raw:
                continue
            command = self.router.parse(raw)
            if command is not None:
                if command.name == "quit":
                    return 0
                if command.name == "help":
                    self.renderer.info(
                        "/help /debug on|off /trace last /tools /memory search <query> "
                        "/approve <token> /deny <token> /quit"
                    )
                    continue
                if command.name == "debug" and command.args:
                    debug = command.args[0].lower() == "on"
                    self.renderer.info(f"debug={'on' if debug else 'off'}")
                    continue
                if command.name == "trace":
                    self.renderer.assistant(self.trace_presenter.present(self.trace_controller.last()))
                    continue
                if command.name == "tools":
                    self.renderer.assistant(self.tool_presenter.present(self.tool_controller.list()))
                    continue
                if command.name == "memory" and command.args[:1] == ["search"] and len(command.args) >= 2:
                    query = " ".join(command.args[1:])
                    self.renderer.assistant(self.memory_presenter.present(self.memory_controller.search(query)))
                    continue
                if command.name == "approve" and command.args:
                    record = self.approval_controller.approve(command.args[0])
                    self.renderer.assistant(self.approval_presenter.present(record, "approved"))
                    continue
                if command.name == "deny" and command.args:
                    record = self.approval_controller.deny(command.args[0])
                    self.renderer.assistant(self.approval_presenter.present(record, "denied"))
                    continue
                self.renderer.error(f"unknown command: /{command.name}")
                continue
            response = await self.chat_controller.submit(session_id=session_id, message=raw, debug=debug)
            session_id = response.session_id
            self.renderer.assistant(self.chat_presenter.present(response))
