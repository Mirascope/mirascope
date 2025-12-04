"""End-to-end tests for behavior when reaching max_tokens limits"""

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_max_tokens_sync(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test synchronous call with token limits."""

    @llm.call(model_id, max_tokens=50)
    def list_states() -> str:
        return "List all U.S. states."

    with snapshot_test(snapshot) as snap:
        response = list_states()
        snap.set_response(response)
        assert response.finish_reason == llm.FinishReason.MAX_TOKENS


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_max_tokens_async(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test asynchronous call with token limits."""

    @llm.call(model_id, max_tokens=50)
    async def list_states() -> str:
        return "List all U.S. states."

    with snapshot_test(snapshot) as snap:
        response = await list_states()
        snap.set_response(response)
        assert response.finish_reason == llm.FinishReason.MAX_TOKENS


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_max_tokens_stream(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test streaming call with token limits."""

    @llm.call(model_id, max_tokens=50)
    def list_states() -> str:
        return "List all U.S. states."

    with snapshot_test(snapshot) as snap:
        response = list_states.stream()
        response.finish()
        snap.set_response(response)
        assert response.finish_reason == llm.FinishReason.MAX_TOKENS


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_max_tokens_async_stream(
    model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming call with token limits."""

    @llm.call(model_id, max_tokens=50)
    async def list_states() -> str:
        return "List all U.S. states."

    with snapshot_test(snapshot) as snap:
        response = await list_states.stream()
        await response.finish()
        snap.set_response(response)
        assert response.finish_reason == llm.FinishReason.MAX_TOKENS
