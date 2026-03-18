from pathlib import Path

import pytest

from sentinel.bootstrap import bootstrap
from sentinel.config.settings import Settings
from tests.fixtures.fake_llm import FakeLLM


@pytest.mark.asyncio
async def test_package_install_guardrails_require_approval(tmp_path: Path) -> None:
    settings = Settings()
    settings.app.data_dir = tmp_path / "data"
    settings.safety.workspace_roots = [str(tmp_path)]
    settings.safety.allow_privileged = False
    settings.ensure_directories()

    llm = FakeLLM(
        plan_queue=[
            {
                "action": "tool",
                "tool_name": "packages.pacman",
                "tool_args": {"operation": "install", "packages": ["ripgrep"], "apply": True},
                "confidence": 0.95,
            }
        ],
        response_queue=["preview only"],
    )
    container = bootstrap(settings=settings, llm_provider=llm)

    response = await container.handle_user_turn.execute(
        __import__("sentinel.application.agent_runtime.dto", fromlist=["HandleTurnRequest"]).HandleTurnRequest(
            session_id=None,
            user_message="Install ripgrep with pacman.",
            debug=True,
        )
    )

    assert response.approvals
    assert response.message == "Action requires approval before execution."
