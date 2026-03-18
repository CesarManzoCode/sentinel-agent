from __future__ import annotations

import httpx
from dataclasses import dataclass

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolInvocation, ToolResult, ToolSpec
from sentinel.infrastructure.tools.base import BaseToolAdapter


@dataclass(slots=True)
class HttpFetcher:
    timeout_seconds: int = 10

    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "sentinel-agent/0.1"})
            response.raise_for_status()
            return response.text


@dataclass(slots=True)
class InternetFetchTool(BaseToolAdapter):
    fetcher: HttpFetcher

    @classmethod
    def create(cls, fetcher: HttpFetcher) -> "InternetFetchTool":
        return cls(
            spec=ToolSpec(
                name="internet.fetch",
                description="Fetch the contents of a URL in read-only mode.",
                category=ToolCategory.INTERNET,
                schema={
                    "type": "object",
                    "properties": {"url": {"type": "string"}},
                    "required": ["url"],
                },
                baseline_risk=RiskLevel.LOW,
                timeout_seconds=15,
                concurrency_safe=True,
                side_effects=("network",),
            ),
            fetcher=fetcher,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        url = str(invocation.arguments["url"])
        text = await self.fetcher.fetch(url)
        return ToolResult(
            invocation_id=invocation.invocation_id,
            tool_name=self.spec.name,
            success=True,
            stdout=text[:32_000],
            metadata={"url": url, "truncated": len(text) > 32_000},
        )
