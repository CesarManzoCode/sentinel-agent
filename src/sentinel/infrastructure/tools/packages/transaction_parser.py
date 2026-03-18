from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PackageTransactionParser:
    def preview(self, operation: str, packages: list[str]) -> str:
        normalized = " ".join(packages)
        if operation == "install":
            return f"pacman -S {normalized}"
        if operation == "remove":
            return f"pacman -R {normalized}"
        if operation == "upgrade":
            return "pacman -Syu"
        if operation == "search":
            return f"pacman -Ss {normalized}"
        if operation == "info":
            return f"pacman -Si {normalized}"
        if operation == "query":
            return f"pacman -Qi {normalized}" if normalized else "pacman -Q"
        return f"unsupported operation: {operation}"
