"""End-to-end tests for behavior when reaching max_tokens limits"""

import pytest

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS, Snapshot
from tests.utils import (
    exception_snapshot_dict,
    response_snapshot_dict,
    stream_response_snapshot_dict,
)


@pytest.mark.parametrize(
    "provider,model_id",
    PROVIDER_MODEL_ID_PAIRS,
)
@pytest.mark.vcr
def test_max_tokens_sync(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test synchronous call with token limits."""

    @llm.call(provider=provider, model_id=model_id, max_tokens=50)
    def list_states() -> str:
        return "List all U.S. states."

    snapshot_data = {}
    try:
        response = list_states()
        snapshot_data["response"] = response_snapshot_dict(response)
        assert response.finish_reason == llm.FinishReason.MAX_TOKENS
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot


@pytest.mark.parametrize(
    "provider,model_id",
    PROVIDER_MODEL_ID_PAIRS,
)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_max_tokens_async(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous call with token limits."""

    @llm.call(provider=provider, model_id=model_id, max_tokens=50)
    async def list_states() -> str:
        return "List all U.S. states."

    snapshot_data = {}
    try:
        response = await list_states()
        snapshot_data["response"] = response_snapshot_dict(response)
        assert response.finish_reason == llm.FinishReason.MAX_TOKENS
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot


@pytest.mark.parametrize(
    "provider,model_id",
    PROVIDER_MODEL_ID_PAIRS,
)
@pytest.mark.vcr
def test_max_tokens_stream(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming call with token limits."""

    @llm.call(provider=provider, model_id=model_id, max_tokens=50)
    def list_states() -> str:
        return "List all U.S. states."

    snapshot_data = {}
    try:
        response = list_states.stream()
        response.finish()
        snapshot_data["response"] = stream_response_snapshot_dict(response)
        assert response.finish_reason == llm.FinishReason.MAX_TOKENS
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot


@pytest.mark.parametrize(
    "provider,model_id",
    PROVIDER_MODEL_ID_PAIRS,
)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_max_tokens_async_stream(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming call with token limits."""

    @llm.call(provider=provider, model_id=model_id, max_tokens=50)
    async def list_states() -> str:
        return "List all U.S. states."

    snapshot_data = {}
    try:
        response = await list_states.stream()
        await response.finish()
        snapshot_data["response"] = stream_response_snapshot_dict(response)
        assert response.finish_reason == llm.FinishReason.MAX_TOKENS
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot
