from __future__ import annotations

import os
import re
from dataclasses import dataclass

from sentinel.domain.safety.entities import IntentScope


_PATH_RE = re.compile(r"(~?/[^\s]+|\./[^\s]+|\.\./[^\s]+)")


@dataclass(slots=True)
class CapabilityScopeService:
    def derive(self, request: str) -> IntentScope:
        verbs = set()
        lowered = request.lower()
        if any(word in lowered for word in ("inspect", "read", "show", "diagnose", "debug", "check", "search")):
            verbs.add("read")
        if any(word in lowered for word in ("write", "edit", "modify", "patch", "update", "create")):
            verbs.add("write")
        if any(word in lowered for word in ("install", "remove", "upgrade", "package")):
            verbs.add("package")
        if any(word in lowered for word in ("web", "internet", "search online", "fetch url")):
            verbs.add("network")
        allowed_paths = {os.path.expanduser(match) for match in _PATH_RE.findall(request)}
        allowed_tools = set()
        if "package" in verbs:
            allowed_tools.add("packages.pacman")
        if "write" in verbs:
            allowed_tools.update({"filesystem.writer", "filesystem.navigator", "filesystem.reader"})
        if "read" in verbs:
            allowed_tools.update({"filesystem.reader", "filesystem.navigator", "system.env", "system.logs", "terminal.exec"})
        if "network" in verbs:
            allowed_tools.update({"internet.search", "internet.fetch"})
        return IntentScope(
            raw_request=request,
            allowed_paths=allowed_paths,
            allowed_verbs=verbs or {"read"},
            allowed_tools=allowed_tools,
        )
