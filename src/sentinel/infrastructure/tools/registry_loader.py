from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from sentinel.config.settings import Settings
from sentinel.domain.tools.entities import ToolSpec
from sentinel.domain.tools.ports import ToolAdapterPort, ToolCatalogPort, ToolRegistryPort
from sentinel.infrastructure.tools.filesystem.navigator import FilesystemNavigatorTool
from sentinel.infrastructure.tools.filesystem.path_policy import PathPolicy
from sentinel.infrastructure.tools.filesystem.reader import FilesystemReaderTool
from sentinel.infrastructure.tools.filesystem.writer import FilesystemWriterTool
from sentinel.infrastructure.tools.internet.fetcher import HttpFetcher, InternetFetchTool
from sentinel.infrastructure.tools.internet.search_provider import InternetSearchProvider, InternetSearchTool
from sentinel.infrastructure.tools.packages.pacman_manager import PacmanManager
from sentinel.infrastructure.tools.packages.transaction_parser import PackageTransactionParser
from sentinel.infrastructure.tools.system.env_inspector import EnvironmentInspectorTool
from sentinel.infrastructure.tools.system.log_reader import LogReaderTool
from sentinel.infrastructure.tools.system.process_inspector import ProcessInspectorTool
from sentinel.infrastructure.tools.terminal.executor import TerminalExecutor
from sentinel.infrastructure.tools.terminal.parser import CommandParser
from sentinel.infrastructure.tools.terminal.sandbox import CommandSandbox


@dataclass(slots=True)
class LoadedToolRegistry(ToolRegistryPort):
    adapters: dict[str, ToolAdapterPort] = field(default_factory=dict)

    def list_tools(self) -> list[ToolSpec]:
        return [adapter.spec for adapter in self.adapters.values()]

    def get_tool(self, name: str) -> ToolAdapterPort | None:
        return self.adapters.get(name)


@dataclass(slots=True)
class ToolRegistryLoader:
    settings: Settings
    catalog: ToolCatalogPort

    def load(self) -> LoadedToolRegistry:
        roots = [Path(root).expanduser().resolve() for root in self.settings.safety.workspace_roots]
        path_policy = PathPolicy(allowed_roots=roots)
        sandbox = CommandSandbox(
            allow_bwrap=self.settings.safety.enable_bwrap,
            env_allowlist={"PATH", "HOME", "LANG", "LC_ALL", "TERM"},
            workspace_roots=roots,
        )

        adapters: list[ToolAdapterPort] = [
            TerminalExecutor.create(CommandParser(), sandbox, path_policy),
            FilesystemNavigatorTool.create(path_policy),
            FilesystemReaderTool.create(path_policy),
            FilesystemWriterTool.create(path_policy),
            EnvironmentInspectorTool.create(),
            ProcessInspectorTool.create(),
            LogReaderTool.create(path_policy),
            InternetSearchTool.create(InternetSearchProvider()),
            InternetFetchTool.create(HttpFetcher()),
            PacmanManager.create(PackageTransactionParser(), allow_privileged=self.settings.safety.allow_privileged),
        ]
        for adapter in adapters:
            self.catalog.save_tool(adapter.spec)
        return LoadedToolRegistry({adapter.spec.name: adapter for adapter in adapters})
