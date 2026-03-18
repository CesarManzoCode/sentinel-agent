import os

import pytest

from sentinel.domain.llm.value_objects import PromptEnvelope
from sentinel.infrastructure.llm.groq_client import GroqLLMClient
from sentinel.infrastructure.llm.response_parser import ProviderResponseParser
from sentinel.infrastructure.llm.stream_adapter import LLMStreamAdapter


pytestmark = pytest.mark.skipif(
    not os.getenv("SENTINEL_GROQ_API_KEY"),
    reason="real Groq API key required",
)


@pytest.mark.asyncio
async def test_groq_streaming_integration() -> None:
    client = GroqLLMClient(
        api_key=os.environ["SENTINEL_GROQ_API_KEY"],
        model=os.getenv("SENTINEL_GROQ_MODEL", "llama-3.1-8b-instant"),
        base_url=os.getenv("SENTINEL_GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        timeout_seconds=30,
        parser=ProviderResponseParser(),
        stream_adapter=LLMStreamAdapter(),
    )
    prompt = PromptEnvelope(system="You are a test assistant.", user="Respond with exactly: ok")
    chunks = []
    async for chunk in client.stream(prompt):
        chunks.append(chunk)
        if len("".join(chunks)) >= 2:
            break
    assert "".join(chunks).strip()
