from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.memory.memory_packager import MemoryPackager
from sentinel.application.memory.retrieval_service import MemoryRetrievalService
from sentinel.application.tools.registry import ToolRegistryService
from sentinel.domain.agent.entities import AgentSession


@dataclass(slots=True)
class ContextBuilder:
    memory_retrieval: MemoryRetrievalService
    memory_packager: MemoryPackager
    tool_registry: ToolRegistryService

    async def build(self, session: AgentSession, user_message: str, top_k: int) -> dict[str, object]:
        memories = await self.memory_retrieval.retrieve(user_message, top_k)
        packaged_memories = self.memory_packager.package(memories)
        tools = self.tool_registry.list_enabled()
        return {
            "summary": session.summary,
            "memories": memories,
            "memory_snippets": packaged_memories,
            "tools": tools,
        }
