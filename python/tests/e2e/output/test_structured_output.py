"""End-to-end tests for structured output."""

import pytest
from pydantic import BaseModel, Field

from mirascope import llm
from tests.e2e.conftest import FORMATTING_MODES, PROVIDER_MODEL_ID_PAIRS
from tests.utils import (
    Snapshot,
    snapshot_test,
)


class Author(BaseModel):
    """The author of a book."""

    first_name: str
    last_name: str


class Book(BaseModel):
    """A book with a rating. The title should be in all caps!"""

    title: str
    author: Author
    rating: int = Field(description="For testing purposes, the rating should be 7")


# ============= SYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_sync(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test synchronous structured output without context."""

    format = (
        llm.format(Book, mode=formatting_mode) if formatting_mode is not None else Book
    )

    @llm.call(
        model_id=model_id,
        format=format,
    )
    def recommend_book(author: str) -> str:
        return f"Please recommend the most popular book by {author}"

    with snapshot_test(snapshot) as snap:
        response = recommend_book("Patrick Rothfuss")
        snap.set_response(response)

        book = response.parse()
        assert book.author.first_name == "Patrick"
        assert book.author.last_name == "Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_sync_context(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test synchronous structured output with context."""

    format = (
        llm.format(Book, mode=formatting_mode) if formatting_mode is not None else Book
    )

    @llm.call(
        model_id=model_id,
        format=format,
    )
    def recommend_book(ctx: llm.Context[str]) -> str:
        return f"Please recommend the most popular book by {ctx.deps}"

    ctx = llm.Context(deps="Patrick Rothfuss")
    with snapshot_test(snapshot) as snap:
        response = recommend_book(ctx)
        snap.set_response(response)

        book = response.parse()
        assert book.author.first_name == "Patrick"
        assert book.author.last_name == "Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_async(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test asynchronous structured output without context."""

    format = (
        llm.format(Book, mode=formatting_mode) if formatting_mode is not None else Book
    )

    @llm.call(
        model_id=model_id,
        format=format,
    )
    async def recommend_book(author: str) -> str:
        return f"Please recommend the most popular book by {author}"

    with snapshot_test(snapshot) as snap:
        response = await recommend_book("Patrick Rothfuss")
        snap.set_response(response)

        book = response.parse()
        assert book.author.first_name == "Patrick"
        assert book.author.last_name == "Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_async_context(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test asynchronous structured output with context."""

    format = (
        llm.format(Book, mode=formatting_mode) if formatting_mode is not None else Book
    )

    @llm.call(
        model_id=model_id,
        format=format,
    )
    async def recommend_book(ctx: llm.Context[str]) -> str:
        return f"Please recommend the most popular book by {ctx.deps}"

    ctx = llm.Context(deps="Patrick Rothfuss")
    with snapshot_test(snapshot) as snap:
        response = await recommend_book(ctx)
        snap.set_response(response)

        book = response.parse()
        assert book.author.first_name == "Patrick"
        assert book.author.last_name == "Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7


# ============= STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_stream(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test streaming structured output without context."""

    format = (
        llm.format(Book, mode=formatting_mode) if formatting_mode is not None else Book
    )

    @llm.call(
        model_id=model_id,
        format=format,
    )
    def recommend_book(author: str) -> str:
        return f"Please recommend the most popular book by {author}"

    with snapshot_test(snapshot) as snap:
        response = recommend_book.stream("Patrick Rothfuss")
        response.finish()

        snap.set_response(response)

        book = response.parse()
        assert book.author.first_name == "Patrick"
        assert book.author.last_name == "Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_stream_context(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test streaming structured output with context."""

    format = (
        llm.format(Book, mode=formatting_mode) if formatting_mode is not None else Book
    )

    @llm.call(
        model_id=model_id,
        format=format,
    )
    def recommend_book(ctx: llm.Context[str]) -> str:
        return f"Please recommend the most popular book by {ctx.deps}"

    ctx = llm.Context(deps="Patrick Rothfuss")
    with snapshot_test(snapshot) as snap:
        response = recommend_book.stream(ctx)
        response.finish()

        snap.set_response(response)

        book = response.parse()
        assert book.author.first_name == "Patrick"
        assert book.author.last_name == "Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_async_stream(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test async streaming structured output without context."""

    format = (
        llm.format(Book, mode=formatting_mode) if formatting_mode is not None else Book
    )

    @llm.call(
        model_id=model_id,
        format=format,
    )
    async def recommend_book(author: str) -> str:
        return f"Please recommend the most popular book by {author}"

    with snapshot_test(snapshot) as snap:
        response = await recommend_book.stream("Patrick Rothfuss")
        await response.finish()

        snap.set_response(response)

        book = response.parse()
        assert book.author.first_name == "Patrick"
        assert book.author.last_name == "Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_async_stream_context(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test async streaming structured output with context."""

    format = (
        llm.format(Book, mode=formatting_mode) if formatting_mode is not None else Book
    )

    @llm.call(
        model_id=model_id,
        format=format,
    )
    async def recommend_book(ctx: llm.Context[str]) -> str:
        return f"Please recommend the most popular book by {ctx.deps}"

    ctx = llm.Context(deps="Patrick Rothfuss")
    with snapshot_test(snapshot) as snap:
        response = await recommend_book.stream(ctx)
        await response.finish()

        snap.set_response(response)

        book = response.parse()
        assert book.author.first_name == "Patrick"
        assert book.author.last_name == "Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7
