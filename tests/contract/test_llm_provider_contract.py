import pytest

from sentinel.domain.llm.value_objects import PromptEnvelope
from tests.fixtures.fake_llm import FakeLLM


@pytest.mark.asyncio
async def test_fake_llm_satisfies_provider_contract() -> None:
    provider = FakeLLM(
        plan_queue=[{"action": "respond", "response": "ok", "confidence": 1.0}],
        response_queue=["ok"],
    )
    prompt = PromptEnvelope(system="system", user="user")
    text, usage = await provider.complete(prompt)
    payload, json_usage = await provider.complete_json(prompt, schema={})

    assert text == "ok"
    assert payload["action"] == "respond"
    assert usage.total_tokens > 0
    assert json_usage.total_tokens > 0
