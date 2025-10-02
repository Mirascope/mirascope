"""End-to-end tests for a LLM call without tools or structured outputs."""

import pytest

from mirascope import llm
from tests.e2e.conftest import (
    PROVIDER_MODEL_ID_PAIRS,
    Snapshot,
)
from tests.utils import response_snapshot_dict, stream_response_snapshot_dict

# ============= SYNC TESTS =============


@pytest.mark.parametrize(
    "provider,model_id",
    PROVIDER_MODEL_ID_PAIRS,
)
@pytest.mark.vcr
def test_call_sync(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test synchronous call without context."""

    @llm.call(provider=provider, model_id=model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    response = add_numbers(4200, 42)

    assert response_snapshot_dict(response) == snapshot
    assert "4242" in response.pretty(), (
        f"Expected '4242' in response: {response.pretty()}"
    )


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_sync_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test synchronous call with context."""

    @llm.call(provider=provider, model_id=model_id)
    def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    ctx = llm.Context(deps=4200)
    response = add_numbers(ctx, 42)

    assert response_snapshot_dict(response) == snapshot
    assert "4242" in response.pretty(), (
        f"Expected '4242' in response: {response.pretty()}"
    )


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_async(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous call without context."""

    @llm.call(provider=provider, model_id=model_id)
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    response = await add_numbers(4200, 42)

    assert response_snapshot_dict(response) == snapshot
    assert "4242" in response.pretty(), (
        f"Expected '4242' in response: {response.pretty()}"
    )


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_async_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous call with context."""

    @llm.call(provider=provider, model_id=model_id)
    async def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    ctx = llm.Context(deps=4200)
    response = await add_numbers(ctx, 42)

    assert response_snapshot_dict(response) == snapshot
    assert "4242" in response.pretty(), (
        f"Expected '4242' in response: {response.pretty()}"
    )


# ============= STREAM TESTS =============


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_stream(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming call without context."""

    @llm.call(provider=provider, model_id=model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    response = add_numbers.stream(4200, 42)
    response.finish()

    assert stream_response_snapshot_dict(response) == snapshot
    assert "4242" in response.pretty(), (
        f"Expected '4242' in response: {response.pretty()}"
    )


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_stream_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming call with context."""

    @llm.call(provider=provider, model_id=model_id)
    def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    ctx = llm.Context(deps=4200)
    response = add_numbers.stream(ctx, 42)
    response.finish()

    assert stream_response_snapshot_dict(response) == snapshot
    assert "4242" in response.pretty(), (
        f"Expected '4242' in response: {response.pretty()}"
    )


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_async_stream(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming call without context."""

    @llm.call(provider=provider, model_id=model_id)
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    response = await add_numbers.stream(4200, 42)
    await response.finish()

    assert stream_response_snapshot_dict(response) == snapshot
    assert "4242" in response.pretty(), (
        f"Expected '4242' in response: {response.pretty()}"
    )


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_async_stream_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming call with context."""

    @llm.call(provider=provider, model_id=model_id)
    async def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    ctx = llm.Context(deps=4200)
    response = await add_numbers.stream(ctx, 42)
    await response.finish()

    assert stream_response_snapshot_dict(response) == snapshot
    assert "4242" in response.pretty(), (
        f"Expected '4242' in response: {response.pretty()}"
    )
