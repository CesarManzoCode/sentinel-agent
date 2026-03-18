from pathlib import Path

import pytest

from sentinel.bootstrap import bootstrap
from sentinel.config.settings import Settings
from tests.fixtures.fake_llm import FakeLLM


@pytest.mark.asyncio
async def test_file_edit_requires_approval_and_then_can_be_reused(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "config.py"
    target.write_text("DEBUG = True\n", encoding="utf-8")

    settings = Settings()
    settings.app.data_dir = tmp_path / "data"
    settings.safety.workspace_roots = [str(workspace)]
    settings.ensure_directories()

    llm = FakeLLM(
        plan_queue=[
            {
                "action": "tool",
                "tool_name": "filesystem.writer",
                "tool_args": {"path": str(target), "content": "DEBUG = False\n"},
                "confidence": 0.9,
            },
            {
                "action": "tool",
                "tool_name": "filesystem.writer",
                "tool_args": {"path": str(target), "content": "DEBUG = False\n"},
                "confidence": 0.9,
            },
            {"action": "respond", "response": "Updated the configuration file.", "confidence": 0.8},
        ],
        response_queue=["Updated the configuration file."],
    )
    container = bootstrap(settings=settings, llm_provider=llm)

    first = await container.handle_user_turn.execute(
        __import__("sentinel.application.agent_runtime.dto", fromlist=["HandleTurnRequest"]).HandleTurnRequest(
            session_id=None,
            user_message=f"Edit {target} to disable debug.",
            debug=True,
        )
    )
    assert first.approvals
    token = first.approvals[0].token
    approved = container.approve_action.approve(token)
    assert approved is not None

    second = await container.handle_user_turn.execute(
        __import__("sentinel.application.agent_runtime.dto", fromlist=["HandleTurnRequest"]).HandleTurnRequest(
            session_id=first.session_id,
            user_message=f"Edit {target} to disable debug.",
            debug=True,
        )
    )
    assert second.message == "Updated the configuration file."
    assert target.read_text(encoding="utf-8") == "DEBUG = False\n"
