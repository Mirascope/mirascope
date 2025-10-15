"""End-to-end tests for LLM call with thinking=True parameter."""

import logging

import pytest

from mirascope import llm
from tests.e2e.conftest import Snapshot
from tests.utils import (
    exception_snapshot_dict,
    response_snapshot_dict,
    stream_response_snapshot_dict,
)

PROVIDER_MODEL_ID_PAIRS: list[tuple[llm.Provider, llm.ModelId]] = [
    ("openai:responses", "gpt-5"),
    ("anthropic", "claude-sonnet-4-0"),
    ("google", "gemini-2.5-flash"),
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

    @llm.call(provider=provider, model_id=model_id, thinking=True)
    def call(query: str) -> str:
        return query

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = call(PROMPT)
            with llm.model(provider=provider, model_id=model_id, thinking=False):
                response = response.resume(RESUME_PROMPT)
            snapshot_data["response"] = response_snapshot_dict(response)
        except Exception as e:
            snapshot_data["exception"] = exception_snapshot_dict(e)

        snapshot_data["logging"] = [
            record.message
            for record in caplog.records
            if record.levelno >= logging.WARNING
        ]
        assert snapshot_data == snapshot


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_thinking_true_stream(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test streaming call with thinking=True to verify reasoning content."""

    @llm.call(provider=provider, model_id=model_id, thinking=True)
    def call(query: str) -> str:
        return query

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = call.stream(PROMPT)
            response.finish()
            with llm.model(provider=provider, model_id=model_id, thinking=False):
                response = response.resume(RESUME_PROMPT)
            response.finish()
            snapshot_data["response"] = stream_response_snapshot_dict(response)
        except Exception as e:
            snapshot_data["exception"] = exception_snapshot_dict(e)

        snapshot_data["logging"] = [
            record.message
            for record in caplog.records
            if record.levelno >= logging.WARNING
        ]
        assert snapshot_data == snapshot


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

    @llm.call(provider=provider, model_id=model_id, thinking=True)
    async def call(query: str) -> str:
        return query

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = await call(PROMPT)
            with llm.model(provider=provider, model_id=model_id, thinking=False):
                response = await response.resume(RESUME_PROMPT)
            snapshot_data["response"] = response_snapshot_dict(response)
        except Exception as e:
            snapshot_data["exception"] = exception_snapshot_dict(e)

        snapshot_data["logging"] = [
            record.message
            for record in caplog.records
            if record.levelno >= logging.WARNING
        ]
        assert snapshot_data == snapshot


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

    @llm.call(provider=provider, model_id=model_id, thinking=True)
    async def call(query: str) -> str:
        return query

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = await call.stream(PROMPT)
            await response.finish()
            with llm.model(provider=provider, model_id=model_id, thinking=False):
                response = await response.resume(RESUME_PROMPT)
            await response.finish()
            snapshot_data["response"] = stream_response_snapshot_dict(response)
        except Exception as e:
            snapshot_data["exception"] = exception_snapshot_dict(e)

        snapshot_data["logging"] = [
            record.message
            for record in caplog.records
            if record.levelno >= logging.WARNING
        ]
        assert snapshot_data == snapshot
