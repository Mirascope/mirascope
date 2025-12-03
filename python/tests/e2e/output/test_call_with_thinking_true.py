"""End-to-end tests for LLM call with thinking=True parameter."""

import pytest

from mirascope import llm
from tests.utils import (
    Snapshot,
    snapshot_test,
)

PROVIDER_MODEL_ID_PAIRS: list[tuple[llm.Provider, llm.ModelId]] = [
    ("openai:responses", "openai:responses/gpt-5"),
    ("anthropic", "anthropic/claude-sonnet-4-0"),
    ("google", "google/gemini-2.5-flash"),
]

# This can't be easily answered without thinking
PROMPT = "How many primes below 400 contain 79 as a substring? Answer ONLY with the number, not sharing which primes they are."
# Check whether the model thinks it retained access to its reasoning process
RESUME_PROMPT = (
    "If you remember what the primes were, then share them, or say 'I don't remember.'"
)


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_thinking_true_sync(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test synchronous call with thinking=True to verify reasoning content."""

    @llm.call(model_id=model_id, thinking=True)
    def call(query: str) -> str:
        return query

    with snapshot_test(snapshot, caplog) as snap:
        response = call(PROMPT)
        with llm.model(provider=provider, model_id=model_id, thinking=False):
            response = response.resume(RESUME_PROMPT)
        snap.set_response(response)


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_thinking_true_stream(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test streaming call with thinking=True to verify reasoning content."""

    @llm.call(model_id=model_id, thinking=True)
    def call(query: str) -> str:
        return query

    with snapshot_test(snapshot, caplog) as snap:
        response = call.stream(PROMPT)
        response.finish()
        with llm.model(provider=provider, model_id=model_id, thinking=False):
            response = response.resume(RESUME_PROMPT)
        response.finish()
        snap.set_response(response)


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_with_thinking_true_async(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test asynchronous call with thinking=True to verify reasoning content."""

    @llm.call(model_id=model_id, thinking=True)
    async def call(query: str) -> str:
        return query

    with snapshot_test(snapshot, caplog) as snap:
        response = await call(PROMPT)
        with llm.model(provider=provider, model_id=model_id, thinking=False):
            response = await response.resume(RESUME_PROMPT)
        snap.set_response(response)


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_with_thinking_true_async_stream(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test async streaming call with thinking=True to verify reasoning content."""

    @llm.call(model_id=model_id, thinking=True)
    async def call(query: str) -> str:
        return query

    with snapshot_test(snapshot, caplog) as snap:
        response = await call.stream(PROMPT)
        await response.finish()
        with llm.model(provider=provider, model_id=model_id, thinking=False):
            response = await response.resume(RESUME_PROMPT)
        await response.finish()
        snap.set_response(response)
