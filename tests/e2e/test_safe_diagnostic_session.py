from pathlib import Path

import pytest

from sentinel.bootstrap import bootstrap
from sentinel.config.settings import Settings
from tests.fixtures.fake_llm import FakeLLM


@pytest.mark.asyncio
async def test_safe_diagnostic_session_end_to_end(tmp_path: Path) -> None:
    settings = Settings()
    settings.app.data_dir = tmp_path / "data"
    settings.safety.workspace_roots = [str(tmp_path)]
    settings.ensure_directories()

    llm = FakeLLM(
        plan_queue=[
            {"action": "tool", "tool_name": "system.env", "tool_args": {}, "confidence": 0.9},
            {"action": "respond", "response": "Your environment is healthy and accessible.", "confidence": 0.8},
        ],
        response_queue=["Your environment is healthy and accessible."],
    )
    container = bootstrap(settings=settings, llm_provider=llm)
    response = await container.handle_user_turn.execute(
        __import__("sentinel.application.agent_runtime.dto", fromlist=["HandleTurnRequest"]).HandleTurnRequest(
            session_id=None,
            user_message="Inspect my environment safely.",
            debug=True,
        )
    )

    assert response.message == "Your environment is healthy and accessible."
    assert any("calling system.env" in event for event in response.tool_events)
