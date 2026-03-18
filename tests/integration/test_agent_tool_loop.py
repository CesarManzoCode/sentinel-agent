from pathlib import Path

import pytest

from sentinel.bootstrap import bootstrap
from sentinel.config.settings import Settings
from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolSpec
from tests.fixtures.fake_llm import FakeLLM
from tests.fixtures.fake_tools import FakeToolRegistry, make_fake_tool


@pytest.mark.asyncio
async def test_agent_orchestrator_runs_tool_then_responds(tmp_path: Path) -> None:
    settings = Settings()
    settings.app.data_dir = tmp_path / "data"
    settings.safety.workspace_roots = [str(tmp_path)]
    settings.ensure_directories()

    fake_tool = make_fake_tool("system.env", category=ToolCategory.SYSTEM)
    registry = FakeToolRegistry({"system.env": fake_tool})
    llm = FakeLLM(
        plan_queue=[
            {
                "action": "tool",
                "tool_name": "system.env",
                "tool_args": {},
                "plan_goal": "inspect environment",
                "confidence": 0.9,
            },
            {
                "action": "respond",
                "response": "The environment looks healthy.",
                "confidence": 0.8,
            },
        ],
        response_queue=["The environment looks healthy."],
    )

    container = bootstrap(settings=settings, llm_provider=llm, tool_registry=registry)
    response = await container.handle_user_turn.execute(
        __import__("sentinel.application.agent_runtime.dto", fromlist=["HandleTurnRequest"]).HandleTurnRequest(
            session_id=None,
            user_message="inspect the environment",
            debug=True,
        )
    )

    assert response.message == "The environment looks healthy."
    assert fake_tool.calls
    assert response.tool_events[0] == "calling system.env"
