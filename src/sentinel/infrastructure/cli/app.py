from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass

from sentinel.bootstrap import bootstrap
from sentinel.infrastructure.cli.chat_loop import ChatLoop
from sentinel.infrastructure.cli.commands import CommandRouter
from sentinel.infrastructure.cli.prompts import PromptFactory
from sentinel.infrastructure.cli.renderer import TerminalRenderer
from sentinel.interfaces.cli.controllers import (
    ApprovalController,
    ChatController,
    MemoryController,
    ToolController,
    TraceController,
)
from sentinel.interfaces.cli.presenters import (
    ApprovalPresenter,
    ChatPresenter,
    MemoryPresenter,
    ToolPresenter,
    TracePresenter,
)


@dataclass(slots=True)
class CLIApp:
    def build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog="sentinel", description="Sentinel local-first terminal AI agent")
        subparsers = parser.add_subparsers(dest="command", required=True)

        subparsers.add_parser("chat", help="start an interactive chat session")
        subparsers.add_parser("tools", help="list enabled tools")

        trace_parser = subparsers.add_parser("trace", help="inspect traces")
        trace_parser.add_argument("--last", action="store_true", help="show the latest trace")

        memory_parser = subparsers.add_parser("memory", help="manage memory")
        memory_sub = memory_parser.add_subparsers(dest="memory_command", required=True)

        memory_search = memory_sub.add_parser("search", help="search memories")
        memory_search.add_argument("query")

        memory_sub.add_parser("recent", help="list recent memories")

        config_parser = subparsers.add_parser("config", help="configuration helpers")
        config_sub = config_parser.add_subparsers(dest="config_command", required=True)
        config_sub.add_parser("validate", help="validate effective configuration")

        return parser

    def run(self, argv: list[str] | None = None) -> int:
        container = bootstrap()
        parser = self.build_parser()
        args = parser.parse_args(argv)

        if args.command == "chat":
            # 👇 CORRECTO: usar settings del container
            renderer = TerminalRenderer(
                use_rich=True,
                debug_mode=container.settings.app.debug,
            )

            loop = ChatLoop(
                chat_controller=ChatController(container.handle_user_turn),
                approval_controller=ApprovalController(container.approve_action),
                trace_controller=TraceController(container.inspect_trace),
                tool_controller=ToolController(container.list_tools),
                memory_controller=MemoryController(container.manage_memory),
                renderer=renderer,
                prompts=PromptFactory(),
                router=CommandRouter(),
                chat_presenter=ChatPresenter(),
                approval_presenter=ApprovalPresenter(),
                trace_presenter=TracePresenter(),
                tool_presenter=ToolPresenter(),
                memory_presenter=MemoryPresenter(),
            )

            return asyncio.run(loop.run())

        if args.command == "tools":
            presenter = ToolPresenter()
            print(presenter.present(container.list_tools.execute()))
            return 0

        if args.command == "trace":
            presenter = TracePresenter()
            print(presenter.present(container.inspect_trace.last()))
            return 0

        if args.command == "memory":
            presenter = MemoryPresenter()

            if args.memory_command == "search":
                print(presenter.present(container.manage_memory.search(args.query)))
                return 0

            if args.memory_command == "recent":
                print(presenter.present(container.manage_memory.recent()))
                return 0

        if args.command == "config" and args.config_command == "validate":
            print(json.dumps(container.settings.as_dict(), indent=2, default=str))
            print(json.dumps(container.health_checker.check(), indent=2, default=str))
            return 0

        parser.error("unknown command")
        return 2


def main(argv: list[str] | None = None) -> int:
    return CLIApp().run(argv)