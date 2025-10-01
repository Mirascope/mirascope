"""End-to-end tests for structured output."""

import pytest
from pydantic import BaseModel

from mirascope import llm
from tests.e2e.conftest import FORMATTING_MODES, PROVIDER_MODEL_ID_PAIRS, Snapshot
from tests.utils import (
    exception_snapshot_dict,
    response_snapshot_dict,
    stream_response_snapshot_dict,
)

BOOK_DB = {
    "0-7653-1178-X": "Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25"
}


class BookSummary(BaseModel):
    title: str
    author: str
    pages: int
    publication_year: int


# ============= SYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_with_tools_sync(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test synchronous structured output with tool calls."""

    @llm.tool
    def get_book_info(isbn: str) -> str:
        """Look up book information by ISBN."""
        return BOOK_DB.get(isbn, "Book not found")

    format = (
        llm.format(BookSummary, mode=formatting_mode)
        if formatting_mode is not None
        else BookSummary
    )

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=format,
    )
    def analyze_book(isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    try:
        response = analyze_book("0-7653-1178-X")

        assert len(response.tool_calls) == 1
        tool_outputs = response.execute_tools()

        response = response.resume(tool_outputs)

        assert response_snapshot_dict(response) == snapshot

        book_summary = response.parse()
        assert book_summary.title == "Mistborn: The Final Empire"
        assert book_summary.author == "Brandon Sanderson"
        assert book_summary.pages == 544
        assert book_summary.publication_year == 2006
    except (llm.FormattingModeNotSupportedError, llm.FeatureNotSupportedError) as e:
        assert exception_snapshot_dict(e) == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_with_tools_sync_context(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test synchronous structured output with tools and context."""

    @llm.tool
    def get_book_info(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        """Look up book information by ISBN."""
        return ctx.deps.get(isbn, "Book not found")

    format = (
        llm.format(BookSummary, mode=formatting_mode)
        if formatting_mode is not None
        else BookSummary
    )

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=format,
    )
    def analyze_book(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    ctx = llm.Context(deps=BOOK_DB)
    try:
        response = analyze_book(ctx, "0-7653-1178-X")

        assert len(response.tool_calls) == 1
        tool_outputs = response.execute_tools(ctx)

        response = response.resume(ctx, tool_outputs)

        assert response_snapshot_dict(response) == snapshot

        book_summary = response.parse()
        assert book_summary.title == "Mistborn: The Final Empire"
        assert book_summary.author == "Brandon Sanderson"
        assert book_summary.pages == 544
        assert book_summary.publication_year == 2006
    except (llm.FormattingModeNotSupportedError, llm.FeatureNotSupportedError) as e:
        assert exception_snapshot_dict(e) == snapshot


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_tools_async(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test asynchronous structured output with tool calls."""

    @llm.tool
    async def get_book_info(isbn: str) -> str:
        """Look up book information by ISBN."""
        return BOOK_DB.get(isbn, "Book not found")

    format = (
        llm.format(BookSummary, mode=formatting_mode)
        if formatting_mode is not None
        else BookSummary
    )

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=format,
    )
    async def analyze_book(isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    try:
        response = await analyze_book("0-7653-1178-X")

        assert len(response.tool_calls) == 1
        tool_outputs = await response.execute_tools()

        response = await response.resume(tool_outputs)

        assert response_snapshot_dict(response) == snapshot

        book_summary = response.parse()
        assert book_summary.title == "Mistborn: The Final Empire"
        assert book_summary.author == "Brandon Sanderson"
        assert book_summary.pages == 544
        assert book_summary.publication_year == 2006
    except (llm.FormattingModeNotSupportedError, llm.FeatureNotSupportedError) as e:
        assert exception_snapshot_dict(e) == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_tools_async_context(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test asynchronous structured output with tools and context."""

    @llm.tool
    async def get_book_info(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        """Look up book information by ISBN."""
        return ctx.deps.get(isbn, "Book not found")

    format = (
        llm.format(BookSummary, mode=formatting_mode)
        if formatting_mode is not None
        else BookSummary
    )

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=format,
    )
    async def analyze_book(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    ctx = llm.Context(deps=BOOK_DB)
    try:
        response = await analyze_book(ctx, "0-7653-1178-X")

        assert len(response.tool_calls) == 1
        tool_outputs = await response.execute_tools(ctx)

        response = await response.resume(ctx, tool_outputs)

        assert response_snapshot_dict(response) == snapshot

        book_summary = response.parse()
        assert book_summary.title == "Mistborn: The Final Empire"
        assert book_summary.author == "Brandon Sanderson"
        assert book_summary.pages == 544
        assert book_summary.publication_year == 2006
    except (llm.FormattingModeNotSupportedError, llm.FeatureNotSupportedError) as e:
        assert exception_snapshot_dict(e) == snapshot


# ============= STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_with_tools_stream(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test streaming structured output with tool calls."""

    @llm.tool
    def get_book_info(isbn: str) -> str:
        """Look up book information by ISBN."""
        return BOOK_DB.get(isbn, "Book not found")

    format = (
        llm.format(BookSummary, mode=formatting_mode)
        if formatting_mode is not None
        else BookSummary
    )

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=format,
    )
    def analyze_book(isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    try:
        response = analyze_book.stream("0-7653-1178-X")
        response.finish()

        assert len(response.tool_calls) == 1
        tool_outputs = response.execute_tools()

        response = response.resume(tool_outputs)
        response.finish()

        assert stream_response_snapshot_dict(response) == snapshot

        book_summary = response.parse()
        assert book_summary.title == "Mistborn: The Final Empire"
        assert book_summary.author == "Brandon Sanderson"
        assert book_summary.pages == 544
        assert book_summary.publication_year == 2006
    except (llm.FormattingModeNotSupportedError, llm.FeatureNotSupportedError) as e:
        assert exception_snapshot_dict(e) == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_with_tools_stream_context(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test streaming structured output with tools and context."""

    @llm.tool
    def get_book_info(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        """Look up book information by ISBN."""
        return ctx.deps.get(isbn, "Book not found")

    format = (
        llm.format(BookSummary, mode=formatting_mode)
        if formatting_mode is not None
        else BookSummary
    )

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=format,
    )
    def analyze_book(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    ctx = llm.Context(deps=BOOK_DB)
    try:
        response = analyze_book.stream(ctx, "0-7653-1178-X")
        response.finish()

        assert len(response.tool_calls) == 1
        tool_outputs = response.execute_tools(ctx)

        response = response.resume(ctx, tool_outputs)
        response.finish()

        assert stream_response_snapshot_dict(response) == snapshot

        book_summary = response.parse()
        assert book_summary.title == "Mistborn: The Final Empire"
        assert book_summary.author == "Brandon Sanderson"
        assert book_summary.pages == 544
        assert book_summary.publication_year == 2006
    except (llm.FormattingModeNotSupportedError, llm.FeatureNotSupportedError) as e:
        assert exception_snapshot_dict(e) == snapshot


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_tools_async_stream(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test async streaming structured output with tool calls."""

    @llm.tool
    async def get_book_info(isbn: str) -> str:
        """Look up book information by ISBN."""
        return BOOK_DB.get(isbn, "Book not found")

    format = (
        llm.format(BookSummary, mode=formatting_mode)
        if formatting_mode is not None
        else BookSummary
    )

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=format,
    )
    async def analyze_book(isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    try:
        response = await analyze_book.stream("0-7653-1178-X")
        await response.finish()

        assert len(response.tool_calls) == 1
        tool_outputs = await response.execute_tools()

        response = await response.resume(tool_outputs)
        await response.finish()

        assert stream_response_snapshot_dict(response) == snapshot

        book_summary = response.parse()
        assert book_summary.title == "Mistborn: The Final Empire"
        assert book_summary.author == "Brandon Sanderson"
        assert book_summary.pages == 544
        assert book_summary.publication_year == 2006
    except (llm.FormattingModeNotSupportedError, llm.FeatureNotSupportedError) as e:
        assert exception_snapshot_dict(e) == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_tools_async_stream_context(
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test async streaming structured output with tools and context."""

    @llm.tool
    async def get_book_info(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        """Look up book information by ISBN."""
        return ctx.deps.get(isbn, "Book not found")

    format = (
        llm.format(BookSummary, mode=formatting_mode)
        if formatting_mode is not None
        else BookSummary
    )

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=format,
    )
    async def analyze_book(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    ctx = llm.Context(deps=BOOK_DB)
    try:
        response = await analyze_book.stream(ctx, "0-7653-1178-X")
        await response.finish()

        assert len(response.tool_calls) == 1
        tool_outputs = await response.execute_tools(ctx)

        response = await response.resume(ctx, tool_outputs)
        await response.finish()

        assert stream_response_snapshot_dict(response) == snapshot

        book_summary = response.parse()
        assert book_summary.title == "Mistborn: The Final Empire"
        assert book_summary.author == "Brandon Sanderson"
        assert book_summary.pages == 544
        assert book_summary.publication_year == 2006
    except (llm.FormattingModeNotSupportedError, llm.FeatureNotSupportedError) as e:
        assert exception_snapshot_dict(e) == snapshot
