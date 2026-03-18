from pathlib import Path

import pytest

from sentinel.bootstrap import bootstrap
from sentinel.config.settings import Settings
from sentinel.interfaces.cli.controllers import ChatController
from sentinel.interfaces.cli.presenters import ChatPresenter
from tests.fixtures.fake_llm import FakeLLM


@pytest.mark.asyncio
async def test_cli_controller_and_presenter_roundtrip(tmp_path: Path) -> None:
    settings = Settings()
    settings.app.data_dir = tmp_path / "data"
    settings.safety.workspace_roots = [str(tmp_path)]
    settings.ensure_directories()

    llm = FakeLLM(
        plan_queue=[{"action": "respond", "response": "hello from sentinel", "confidence": 0.99}],
        response_queue=["hello from sentinel"],
    )
    container = bootstrap(settings=settings, llm_provider=llm)
    controller = ChatController(container.handle_user_turn)
    presenter = ChatPresenter()

    response = await controller.submit(None, "say hello", debug=True)
    rendered = presenter.present(response)

    assert "hello from sentinel" in rendered
    assert response.session_id.startswith("sess_")
