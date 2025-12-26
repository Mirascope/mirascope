"""End-to-end tests for structured output with FromCallArgs."""

from typing import Annotated

import pytest
from pydantic import BaseModel

from mirascope import llm
from tests.e2e.conftest import STRUCTURED_OUTPUT_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)


class Book(BaseModel):
    """A book with title, author, and summary."""

    title: Annotated[str, llm.FromCallArgs()]
    author: Annotated[str, llm.FromCallArgs()]
    summary: str


# ============= SYNC TESTS =============


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
def test_structured_output_with_from_call_args_sync(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test synchronous structured output with FromCallArgs fields."""

    @llm.call(model_id, format=Book)
    def summarize_book(title: str, author: str) -> str:
        return f"Summarize the book {title} by {author}."

    with snapshot_test(snapshot) as snap:
        response = summarize_book("The Name of the Wind", "Patrick Rothfuss")
        snap.set_response(response)

        book = response.parse()
        assert book.title == "The Name of the Wind"
        assert book.author == "Patrick Rothfuss"
        assert len(book.summary) > 0


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_from_call_args_async(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test asynchronous structured output with FromCallArgs fields."""

    @llm.call(model_id, format=Book)
    async def summarize_book(title: str, author: str) -> str:
        return f"Summarize the book {title} by {author}."

    with snapshot_test(snapshot) as snap:
        response = await summarize_book("The Name of the Wind", "Patrick Rothfuss")
        snap.set_response(response)

        book = response.parse()
        assert book.title == "The Name of the Wind"
        assert book.author == "Patrick Rothfuss"
        assert len(book.summary) > 0


# ============= STREAM TESTS =============


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
def test_structured_output_with_from_call_args_stream(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test streaming structured output with FromCallArgs fields."""

    @llm.call(model_id, format=Book)
    def summarize_book(title: str, author: str) -> str:
        return f"Summarize the book {title} by {author}."

    with snapshot_test(snapshot) as snap:
        response = summarize_book.stream("The Name of the Wind", "Patrick Rothfuss")
        response.finish()

        snap.set_response(response)

        book = response.parse()
        assert book.title == "The Name of the Wind"
        assert book.author == "Patrick Rothfuss"
        assert len(book.summary) > 0


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_from_call_args_async_stream(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test async streaming structured output with FromCallArgs fields."""

    @llm.call(model_id, format=Book)
    async def summarize_book(title: str, author: str) -> str:
        return f"Summarize the book {title} by {author}."

    with snapshot_test(snapshot) as snap:
        response = await summarize_book.stream(
            "The Name of the Wind", "Patrick Rothfuss"
        )
        await response.finish()

        snap.set_response(response)

        book = response.parse()
        assert book.title == "The Name of the Wind"
        assert book.author == "Patrick Rothfuss"
        assert len(book.summary) > 0
