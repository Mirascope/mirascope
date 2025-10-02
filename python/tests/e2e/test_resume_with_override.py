"""End-to-end tests for resuming a LLM call with a different model and provider."""

from typing import TypedDict

import pytest

from mirascope import llm
from tests.e2e.conftest import (
    PROVIDER_MODEL_ID_PAIRS,
    Snapshot,
)
from tests.utils import response_snapshot_dict, stream_response_snapshot_dict


class ProviderAndModelId(TypedDict, total=True):
    provider: llm.Provider
    model_id: llm.ModelId


def default_provider_and_model(
    provider: llm.Provider,
) -> ProviderAndModelId:
    """Default provider and model that are distinct from the provider being tested.

    Used to ensure that we can test having the provider under test resume
    from a response that was created by a different provider.
    """
    if provider == "anthropic":
        return {"provider": "google", "model_id": "gemini-2.5-flash"}
    else:
        return {"provider": "anthropic", "model_id": "claude-sonnet-4-0"}


# ============= SYNC TESTS =============


@pytest.mark.parametrize(
    "provider,model_id",
    PROVIDER_MODEL_ID_PAIRS,
)
@pytest.mark.vcr
def test_resume_with_override_sync(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test synchronous call without context."""

    @llm.call(**default_provider_and_model(provider))
    def who_made_you() -> str:
        return "Who created you?"

    response = who_made_you()

    with llm.model(provider=provider, model_id=model_id):
        response = response.resume("Can you double-check that?")

    assert response_snapshot_dict(response) == snapshot


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_resume_with_override_sync_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test synchronous call with context."""

    @llm.call(**default_provider_and_model(provider))
    def who_made_you(ctx: llm.Context[str]) -> str:
        return "Who created you?"

    ctx = llm.Context(deps="Who created you?")
    response = who_made_you(ctx)

    with llm.model(provider=provider, model_id=model_id):
        response = response.resume(ctx, "Can you double-check that?")

    assert response_snapshot_dict(response) == snapshot


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_resume_with_override_async(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous call without context."""

    @llm.call(**default_provider_and_model(provider))
    async def who_made_you() -> str:
        return "Who created you?"

    response = await who_made_you()

    with llm.model(provider=provider, model_id=model_id):
        response = await response.resume("Can you double-check that?")

    assert response_snapshot_dict(response) == snapshot


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_resume_with_override_async_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous call with context."""

    @llm.call(**default_provider_and_model(provider))
    async def who_made_you(ctx: llm.Context[str]) -> str:
        return ctx.deps

    ctx = llm.Context(deps="Who created you?")
    response = await who_made_you(ctx)

    with llm.model(provider=provider, model_id=model_id):
        response = await response.resume(ctx, "Can you double-check that?")

    assert response_snapshot_dict(response) == snapshot


# ============= STREAM TESTS =============


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_resume_with_override_stream(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming call without context."""

    @llm.call(**default_provider_and_model(provider))
    def who_made_you() -> str:
        return "Who created you?"

    response = who_made_you.stream().finish()

    with llm.model(provider=provider, model_id=model_id):
        response = response.resume("Can you double-check that?").finish()

    assert stream_response_snapshot_dict(response) == snapshot


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_resume_with_override_stream_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming call with context."""

    @llm.call(**default_provider_and_model(provider))
    def who_made_you(ctx: llm.Context[str]) -> str:
        return ctx.deps

    ctx = llm.Context(deps="Who created you?")
    response = who_made_you.stream(ctx).finish()

    with llm.model(provider=provider, model_id=model_id):
        response = response.resume(ctx, "Can you double-check that?").finish()

    assert stream_response_snapshot_dict(response) == snapshot


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_resume_with_override_async_stream(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming call without context."""

    @llm.call(**default_provider_and_model(provider))
    async def who_made_you() -> str:
        return "Who created you?"

    response = await who_made_you.stream()
    await response.finish()

    with llm.model(provider=provider, model_id=model_id):
        response = await response.resume("Can you double-check that?")
    await response.finish()

    assert stream_response_snapshot_dict(response) == snapshot


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_resume_with_override_async_stream_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming call with context."""

    @llm.call(**default_provider_and_model(provider))
    async def who_made_you(ctx: llm.Context[str]) -> str:
        return ctx.deps

    ctx = llm.Context(deps="Who created you?")
    response = await who_made_you.stream(ctx)
    await response.finish()

    with llm.model(provider=provider, model_id=model_id):
        response = await response.resume(ctx, "Can you double-check that?")
    await response.finish()

    assert stream_response_snapshot_dict(response) == snapshot
