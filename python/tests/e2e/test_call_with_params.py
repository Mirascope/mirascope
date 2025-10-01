"""End-to-end tests for a LLM call without tools or structured outputs."""

import logging

import pytest

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS, Snapshot
from tests.utils import (
    exception_snapshot_dict,
    response_snapshot_dict,
    stream_response_snapshot_dict,
)

# ============= ALL PARAMS TESTS =============
ALL_PARAMS: llm.Params = {
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.3,
    "top_k": 50,
    "seed": 42,
    "stop_sequences": ["4242"],
}


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_params_sync(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test synchronous call with all parameters to verify param handling and logging."""

    @llm.call(provider=provider, model_id=model_id, **ALL_PARAMS)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = add_numbers(4200, 42)
            snapshot_data["response"] = (response_snapshot_dict(response),)
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
def test_call_with_params_stream(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test synchronous call with all parameters to verify param handling and logging."""

    @llm.call(provider=provider, model_id=model_id, **ALL_PARAMS)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = add_numbers.stream(4200, 42)
            response.finish()
            snapshot_data["response"] = (stream_response_snapshot_dict(response),)
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
async def test_call_with_params_async(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test asynchronous call with all parameters to verify param handling and logging."""

    @llm.call(provider=provider, model_id=model_id, **ALL_PARAMS)
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = await add_numbers(4200, 42)
            snapshot_data["response"] = (response_snapshot_dict(response),)
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
async def test_call_with_params_async_stream(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test async streaming call with all parameters to verify param handling and logging."""

    @llm.call(provider=provider, model_id=model_id, **ALL_PARAMS)
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = await add_numbers.stream(4200, 42)
            await response.finish()
            snapshot_data["response"] = (stream_response_snapshot_dict(response),)
        except Exception as e:
            snapshot_data["exception"] = exception_snapshot_dict(e)

        snapshot_data["logging"] = [
            record.message
            for record in caplog.records
            if record.levelno >= logging.WARNING
        ]
        assert snapshot_data == snapshot


# ============= MINIMAL PARAMS TESTS =============

MINIMAL_PARAMS: llm.Params = {
    "temperature": 0.7,
    "max_tokens": 120,
    "top_p": 0.3,
}


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_minimal_params_sync(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call with minimal params and low max_tokens (should impact finish reason)."""

    @llm.call(provider=provider, model_id=model_id, **MINIMAL_PARAMS)
    def list_states() -> str:
        return "List all U.S. states"

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = list_states()
            snapshot_data["response"] = (response_snapshot_dict(response),)
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
def test_call_with_minimal_params_stream(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a stream with minimal params and low max_tokens (should impact finish reason)."""

    @llm.call(provider=provider, model_id=model_id, **MINIMAL_PARAMS)
    def list_states() -> str:
        return "List all U.S. states"

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = list_states.stream()
            response.finish()
            snapshot_data["response"] = (stream_response_snapshot_dict(response),)
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
async def test_call_with_minimal_params_async(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test async call with minimal params and low max_tokens (should impact finish reason)."""

    @llm.call(provider=provider, model_id=model_id, **MINIMAL_PARAMS)
    async def list_states() -> str:
        return "List all U.S. states"

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = await list_states()
            snapshot_data["response"] = (response_snapshot_dict(response),)
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
async def test_call_with_minimal_params_async_stream(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test async stream with minimal params and low max_tokens (should impact finish reason)."""

    @llm.call(provider=provider, model_id=model_id, **MINIMAL_PARAMS)
    async def list_states() -> str:
        return "List all U.S. states"

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = await list_states.stream()
            await response.finish()
            snapshot_data["response"] = (stream_response_snapshot_dict(response),)
        except Exception as e:
            snapshot_data["exception"] = exception_snapshot_dict(e)

        snapshot_data["logging"] = [
            record.message
            for record in caplog.records
            if record.levelno >= logging.WARNING
        ]
        assert snapshot_data == snapshot
