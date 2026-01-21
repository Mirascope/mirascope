"""End-to-end tests for a LLM call without tools or structured outputs."""

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)

# ============= SYNC TESTS =============


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_sync(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test synchronous call without context."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_sync_context(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test synchronous call with context."""

    @llm.call(model_id)
    def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    with snapshot_test(snapshot) as snap:
        ctx = llm.Context(deps=4200)
        response = add_numbers(ctx, 42)
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_async(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test asynchronous call without context."""

    @llm.call(model_id)
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    with snapshot_test(snapshot) as snap:
        response = await add_numbers(4200, 42)
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_async_context(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test asynchronous call with context."""

    @llm.call(model_id)
    async def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    with snapshot_test(snapshot) as snap:
        ctx = llm.Context(deps=4200)
        response = await add_numbers(ctx, 42)
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


# ============= STREAM TESTS =============


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_stream(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test streaming call without context."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    with snapshot_test(snapshot) as snap:
        response = add_numbers.stream(4200, 42)
        response.finish()
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_stream_context(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test streaming call with context."""

    @llm.call(model_id)
    def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    with snapshot_test(snapshot) as snap:
        ctx = llm.Context(deps=4200)
        response = add_numbers.stream(ctx, 42)
        response.finish()
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_async_stream(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test async streaming call without context."""

    @llm.call(model_id)
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    with snapshot_test(snapshot) as snap:
        response = await add_numbers.stream(4200, 42)
        await response.finish()
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_async_stream_context(
    model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming call with context."""

    @llm.call(model_id)
    async def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    with snapshot_test(snapshot) as snap:
        ctx = llm.Context(deps=4200)
        response = await add_numbers.stream(ctx, 42)
        await response.finish()
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )
