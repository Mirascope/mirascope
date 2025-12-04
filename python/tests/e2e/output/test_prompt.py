"""End-to-end tests for a LLM prompt without tools or structured outputs."""

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
def test_prompt_sync(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test synchronous prompt without context."""

    @llm.prompt
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    with snapshot_test(snapshot) as snap:
        model = llm.Model(model_id)
        response = add_numbers(model, 4200, 42)
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_prompt_sync_context(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test synchronous prompt with context."""

    @llm.prompt
    def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    with snapshot_test(snapshot) as snap:
        model = llm.Model(model_id)
        ctx = llm.Context(deps=4200)
        response = add_numbers(model, ctx, 42)
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_prompt_async(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test asynchronous prompt without context."""

    @llm.prompt
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    with snapshot_test(snapshot) as snap:
        model = llm.Model(model_id)
        response = await add_numbers(model, 4200, 42)
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_prompt_async_context(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test asynchronous prompt with context."""

    @llm.prompt
    async def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    with snapshot_test(snapshot) as snap:
        model = llm.Model(model_id)
        ctx = llm.Context(deps=4200)
        response = await add_numbers(model, ctx, 42)
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


# ============= STREAM TESTS =============


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_prompt_stream(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test streaming prompt without context."""

    @llm.prompt
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    with snapshot_test(snapshot) as snap:
        model = llm.Model(model_id)
        response = add_numbers.stream(model, 4200, 42)
        response.finish()
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_prompt_stream_context(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test streaming prompt with context."""

    @llm.prompt
    def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    with snapshot_test(snapshot) as snap:
        model = llm.Model(model_id)
        ctx = llm.Context(deps=4200)
        response = add_numbers.stream(model, ctx, 42)
        response.finish()
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_prompt_async_stream(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test async streaming prompt without context."""

    @llm.prompt
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    with snapshot_test(snapshot) as snap:
        model = llm.Model(model_id)
        response = await add_numbers.stream(model, 4200, 42)
        await response.finish()
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_prompt_async_stream_context(
    model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming prompt with context."""

    @llm.prompt
    async def add_numbers(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    with snapshot_test(snapshot) as snap:
        model = llm.Model(model_id)
        ctx = llm.Context(deps=4200)
        response = await add_numbers.stream(model, ctx, 42)
        await response.finish()
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )
