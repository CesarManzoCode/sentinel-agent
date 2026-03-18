from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from urllib.parse import quote

import httpx

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolInvocation, ToolResult, ToolSpec
from sentinel.infrastructure.tools.base import BaseToolAdapter


_RESULT_RE = re.compile(
    r'<a[^>]+class="result__a"[^>]+href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>',
    re.IGNORECASE,
)


@dataclass(slots=True)
class InternetSearchProvider:
    timeout_seconds: int = 10

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, str]]:
        url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "sentinel-agent/0.1"})
            response.raise_for_status()
        matches = _RESULT_RE.findall(response.text)
        results: list[dict[str, str]] = []
        for href, title in matches[:max_results]:
            results.append({"title": html.unescape(re.sub(r"<.*?>", "", title)), "url": href})
        return results


@dataclass(slots=True)
class InternetSearchTool(BaseToolAdapter):
    provider: InternetSearchProvider

    @classmethod
    def create(cls, provider: InternetSearchProvider) -> "InternetSearchTool":
        return cls(
            spec=ToolSpec(
                name="internet.search",
                description="Search the web and return normalized results with titles and URLs.",
                category=ToolCategory.INTERNET,
                schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "max_results": {"type": "integer"},
                    },
                    "required": ["query"],
                },
                baseline_risk=RiskLevel.LOW,
                timeout_seconds=15,
                concurrency_safe=True,
                side_effects=("network",),
            ),
            provider=provider,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        query = str(invocation.arguments["query"])
        max_results = int(invocation.arguments.get("max_results", 5))
        results = await self.provider.search(query, max_results=max_results)
        return ToolResult(
            invocation_id=invocation.invocation_id,
            tool_name=self.spec.name,
            success=True,
            stdout=json.dumps(results, ensure_ascii=False, indent=2),
        )
