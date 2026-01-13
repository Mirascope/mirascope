"""End-to-end tests for structured output streaming."""

from typing import Any

import pytest
from pydantic import BaseModel

from mirascope import llm
from tests.utils import (
    Snapshot,
    SnapshotDict,
    snapshot_test,
)

# This behavior is largely model-agnostic, so we will test on just one model
# to reduce test bloat.
MODEL_IDS = ["anthropic/claude-haiku-4-5"]


class BookReview(BaseModel):
    title: str
    author: str
    themes: list[str]
    rating: int


def set_structured_stream(snap: SnapshotDict, partials: list[Any]) -> None:
    """Add structured stream partials to the snapshot."""
    partials = [partial.model_dump() if partial else partial for partial in partials]
    snap["structured_stream"] = partials


@pytest.mark.parametrize("model_id", MODEL_IDS)
@pytest.mark.vcr
def test_structured_stream_sync(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test sync structured streaming with BaseModel format."""

    @llm.call(model_id, format=BookReview)
    def recommend_book() -> str:
        return "Please recommend a book to me!"

    with snapshot_test(snapshot) as snap:
        response = recommend_book.stream()

        partials = list(response.structured_stream())

        snap.set_response(response)
        set_structured_stream(snap, partials)


@pytest.mark.parametrize("model_id", MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_stream_async(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test async structured streaming with BaseModel format."""

    @llm.call(model_id, format=BookReview)
    async def recommend_book() -> str:
        return "Please recommend a book to me!"

    with snapshot_test(snapshot) as snap:
        response = await recommend_book.stream()

        partials = [p async for p in response.structured_stream()]

        snap.set_response(response)
        set_structured_stream(snap, partials)
