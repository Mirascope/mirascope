"""End-to-end tests for behavior when reaching max_tokens limits"""

import pytest

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS
from tests.utils import Snapshot, snapshot_test


def _assert_finish_reason(response: object) -> None:
    """Assert that the response indicates it respected the max_tokens limit.

    Some providers (notably xAI Grok as of October 2025) do not currently
    populate a FinishReason when the server stops generation at the requested
    max_tokens. In that case we accept `None` but still cover it in snapshots.
    """
    provider = getattr(response, "provider", None)
    finish_reason = getattr(response, "finish_reason", None)
    if provider == "xai" and finish_reason is None:
        return
    assert finish_reason == llm.FinishReason.MAX_TOKENS


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

    with snapshot_test(snapshot) as snap:
        response = list_states()
        snap.set_response(response)
        _assert_finish_reason(response)


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

    with snapshot_test(snapshot) as snap:
        response = await list_states()
        snap.set_response(response)
        _assert_finish_reason(response)


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

    with snapshot_test(snapshot) as snap:
        response = list_states.stream()
        response.finish()
        snap.set_response(response)
        _assert_finish_reason(response)


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

    with snapshot_test(snapshot) as snap:
        response = await list_states.stream()
        await response.finish()
        snap.set_response(response)
        _assert_finish_reason(response)
