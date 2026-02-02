"""End-to-end tests for structured output with validation retry using response.validate()."""

import pytest
from pydantic import BaseModel, field_validator

from mirascope import llm
from tests.e2e.conftest import STRUCTURED_OUTPUT_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)


class LuckyNumber(BaseModel):
    """A lucky number chosen by the model."""

    value: int

    @field_validator("value")
    @classmethod
    def must_be_173(cls, v: int) -> int:
        """Validate that the number is exactly 173.

        This constraint is NOT in the schema, so the LLM won't know about it
        on the first attempt, forcing a validation retry.
        """
        if v != 173:
            raise ValueError(f"The number must be exactly 173, but got {v}")
        return v


# ============= SYNC TESTS =============


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
def test_validation_retry_sync(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that validate() retries on parse error and succeeds after LLM correction."""

    @llm.call(
        model_id,
        format=llm.format(LuckyNumber, mode="json"),
    )
    def pick_number() -> str:
        return "Pick a random number between 1 and 1000"

    with snapshot_test(snapshot) as snap:
        response = pick_number()

        # validate() should retry when the number isn't 173
        number, final_response = response.validate(max_retries=1)

        snap.set_response(final_response)

        assert number is not None
        assert number.value == 173


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
def test_validation_retry_sync_context(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that validate() works with context responses."""

    @llm.call(
        model_id,
        format=llm.format(LuckyNumber, mode="json"),
    )
    def pick_number(ctx: llm.Context[None]) -> str:
        return "Pick a random number between 1 and 1000"

    ctx = llm.Context(deps=None)
    with snapshot_test(snapshot) as snap:
        response = pick_number(ctx)

        number, final_response = response.validate(ctx, max_retries=1)

        snap.set_response(final_response)

        assert number is not None
        assert number.value == 173


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_validation_retry_async(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that async validate() retries on parse error and succeeds after LLM correction."""

    @llm.call(
        model_id,
        format=llm.format(LuckyNumber, mode="json"),
    )
    async def pick_number() -> str:
        return "Pick a random number between 1 and 1000"

    with snapshot_test(snapshot) as snap:
        response = await pick_number()

        number, final_response = await response.validate(max_retries=1)

        snap.set_response(final_response)

        assert number is not None
        assert number.value == 173


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_validation_retry_async_context(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that async validate() works with context responses."""

    @llm.call(
        model_id,
        format=llm.format(LuckyNumber, mode="json"),
    )
    async def pick_number(ctx: llm.Context[None]) -> str:
        return "Pick a random number between 1 and 1000"

    ctx = llm.Context(deps=None)
    with snapshot_test(snapshot) as snap:
        response = await pick_number(ctx)

        number, final_response = await response.validate(ctx, max_retries=1)

        snap.set_response(final_response)

        assert number is not None
        assert number.value == 173


# ============= STREAM TESTS =============


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
def test_validation_retry_stream(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that stream validate() retries on parse error."""

    @llm.call(
        model_id,
        format=llm.format(LuckyNumber, mode="json"),
    )
    def pick_number() -> str:
        return "Pick a random number between 1 and 1000"

    with snapshot_test(snapshot) as snap:
        response = pick_number.stream()

        # validate() consumes the stream and retries if needed
        number, final_response = response.validate(max_retries=1)

        snap.set_response(final_response)

        assert number is not None
        assert number.value == 173


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
def test_validation_retry_stream_context(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that stream validate() works with context responses."""

    @llm.call(
        model_id,
        format=llm.format(LuckyNumber, mode="json"),
    )
    def pick_number(ctx: llm.Context[None]) -> str:
        return "Pick a random number between 1 and 1000"

    ctx = llm.Context(deps=None)
    with snapshot_test(snapshot) as snap:
        response = pick_number.stream(ctx)

        number, final_response = response.validate(ctx, max_retries=1)

        snap.set_response(final_response)

        assert number is not None
        assert number.value == 173


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_validation_retry_async_stream(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that async stream validate() retries on parse error."""

    @llm.call(
        model_id,
        format=llm.format(LuckyNumber, mode="json"),
    )
    async def pick_number() -> str:
        return "Pick a random number between 1 and 1000"

    with snapshot_test(snapshot) as snap:
        response = await pick_number.stream()

        number, final_response = await response.validate(max_retries=1)

        snap.set_response(final_response)

        assert number is not None
        assert number.value == 173


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_validation_retry_async_stream_context(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that async stream validate() works with context responses."""

    @llm.call(
        model_id,
        format=llm.format(LuckyNumber, mode="json"),
    )
    async def pick_number(ctx: llm.Context[None]) -> str:
        return "Pick a random number between 1 and 1000"

    ctx = llm.Context(deps=None)
    with snapshot_test(snapshot) as snap:
        response = await pick_number.stream(ctx)

        number, final_response = await response.validate(ctx, max_retries=1)

        snap.set_response(final_response)

        assert number is not None
        assert number.value == 173
