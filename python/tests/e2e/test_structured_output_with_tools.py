"""End-to-end tests for structured output."""

from typing import Annotated

import pytest
from pydantic import BaseModel, Field

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS, Snapshot
from tests.utils import response_snapshot_dict, stream_response_snapshot_dict

BOOK_DB = {
    "0-7653-1178-X": "Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25"
}

# ============= SYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_structured_output_with_tools_sync(
    provider: llm.clients.Provider,
    model_id: llm.clients.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test synchronous structured output with tool calls."""

    @llm.tool
    def get_book_info(isbn: str) -> str:
        """Look up book information by ISBN."""
        return BOOK_DB.get(isbn, "Book not found")

    class BookSummary(BaseModel):
        title: str
        author: str
        pages: int
        publication_year: int
        recommendation_score: Annotated[
            int, Field(description="Should be 7 for testing purposes")
        ]

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=BookSummary,
    )
    def analyze_book(isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    response = analyze_book("0-7653-1178-X")
    assert len(response.tool_calls) == 1

    tool_outputs = response.execute_tools()
    response = response.resume(tool_outputs)

    assert response_snapshot_dict(response) == snapshot

    book_summary = response.format()
    assert book_summary.title == "Mistborn: The Final Empire"
    assert book_summary.author == "Brandon Sanderson"
    assert book_summary.pages == 544
    assert book_summary.publication_year == 2006
    assert book_summary.recommendation_score == 7


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_structured_output_with_tools_sync_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test synchronous structured output with tools and context."""

    @llm.context_tool
    def get_book_info(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        """Look up book information by ISBN."""
        return ctx.deps.get(isbn, "Book not found")

    class BookSummary(BaseModel):
        title: str
        author: str
        pages: int
        publication_year: int
        recommendation_score: Annotated[
            int, Field(description="Should be 7 for testing purposes")
        ]

    @llm.context_call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=BookSummary,
    )
    def analyze_book(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    ctx = llm.Context(deps=BOOK_DB)
    response = analyze_book(ctx, "0-7653-1178-X")
    assert len(response.tool_calls) == 1

    tool_outputs = response.execute_tools(ctx)
    response = response.resume(ctx, tool_outputs)

    assert response_snapshot_dict(response) == snapshot

    book_summary = response.format()
    assert book_summary.title == "Mistborn: The Final Empire"
    assert book_summary.author == "Brandon Sanderson"
    assert book_summary.pages == 544
    assert book_summary.publication_year == 2006
    assert book_summary.recommendation_score == 7


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_tools_async(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous structured output with tool calls."""

    @llm.tool
    async def get_book_info(isbn: str) -> str:
        """Look up book information by ISBN."""
        return BOOK_DB.get(isbn, "Book not found")

    class BookSummary(BaseModel):
        title: str
        author: str
        pages: int
        publication_year: int
        recommendation_score: Annotated[
            int, Field(description="Should be 7 for testing purposes")
        ]

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=BookSummary,
    )
    async def analyze_book(isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    response = await analyze_book("0-7653-1178-X")
    assert len(response.tool_calls) == 1

    tool_outputs = await response.execute_tools()
    response = await response.resume(tool_outputs)

    assert response_snapshot_dict(response) == snapshot

    book_summary = response.format()
    assert book_summary.title == "Mistborn: The Final Empire"
    assert book_summary.author == "Brandon Sanderson"
    assert book_summary.pages == 544
    assert book_summary.publication_year == 2006
    assert book_summary.recommendation_score == 7


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_tools_async_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous structured output with tools and context."""

    @llm.context_tool
    async def get_book_info(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        """Look up book information by ISBN."""
        return ctx.deps.get(isbn, "Book not found")

    class BookSummary(BaseModel):
        title: str
        author: str
        pages: int
        publication_year: int
        recommendation_score: Annotated[
            int, Field(description="Should be 7 for testing purposes")
        ]

    @llm.context_call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=BookSummary,
    )
    async def analyze_book(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    ctx = llm.Context(deps=BOOK_DB)
    response = await analyze_book(ctx, "0-7653-1178-X")
    assert len(response.tool_calls) == 1

    tool_outputs = await response.execute_tools(ctx)
    response = await response.resume(ctx, tool_outputs)

    assert response_snapshot_dict(response) == snapshot

    book_summary = response.format()
    assert book_summary.title == "Mistborn: The Final Empire"
    assert book_summary.author == "Brandon Sanderson"
    assert book_summary.pages == 544
    assert book_summary.publication_year == 2006
    assert book_summary.recommendation_score == 7


# ============= STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_structured_output_with_tools_stream(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming structured output with tool calls."""

    @llm.tool
    def get_book_info(isbn: str) -> str:
        """Look up book information by ISBN."""
        return BOOK_DB.get(isbn, "Book not found")

    class BookSummary(BaseModel):
        title: str
        author: str
        pages: int
        publication_year: int
        recommendation_score: Annotated[
            int, Field(description="Should be 7 for testing purposes")
        ]

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=BookSummary,
    )
    def analyze_book(isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    response = analyze_book.stream("0-7653-1178-X")

    for _ in response.chunk_stream():
        pass

    assert len(response.tool_calls) == 1

    tool_outputs = response.execute_tools()
    response = response.resume(tool_outputs)

    for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot

    book_summary = response.format()
    assert book_summary.title == "Mistborn: The Final Empire"
    assert book_summary.author == "Brandon Sanderson"
    assert book_summary.pages == 544
    assert book_summary.publication_year == 2006
    assert book_summary.recommendation_score == 7


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_structured_output_with_tools_stream_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming structured output with tools and context."""

    @llm.context_tool
    def get_book_info(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        """Look up book information by ISBN."""
        return ctx.deps.get(isbn, "Book not found")

    class BookSummary(BaseModel):
        title: str
        author: str
        pages: int
        publication_year: int
        recommendation_score: Annotated[
            int, Field(description="Should be 7 for testing purposes")
        ]

    @llm.context_call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=BookSummary,
    )
    def analyze_book(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    ctx = llm.Context(deps=BOOK_DB)
    response = analyze_book.stream(ctx, "0-7653-1178-X")

    for _ in response.chunk_stream():
        pass

    assert len(response.tool_calls) == 1

    tool_outputs = response.execute_tools(ctx)
    response = response.resume(ctx, tool_outputs)

    for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot

    book_summary = response.format()
    assert book_summary.title == "Mistborn: The Final Empire"
    assert book_summary.author == "Brandon Sanderson"
    assert book_summary.pages == 544
    assert book_summary.publication_year == 2006
    assert book_summary.recommendation_score == 7


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_tools_async_stream(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming structured output with tool calls."""

    @llm.tool
    async def get_book_info(isbn: str) -> str:
        """Look up book information by ISBN."""
        return BOOK_DB.get(isbn, "Book not found")

    class BookSummary(BaseModel):
        title: str
        author: str
        pages: int
        publication_year: int
        recommendation_score: Annotated[
            int, Field(description="Should be 7 for testing purposes")
        ]

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=BookSummary,
    )
    async def analyze_book(isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    response = await analyze_book.stream("0-7653-1178-X")

    async for _ in response.chunk_stream():
        pass

    assert len(response.tool_calls) == 1

    tool_outputs = await response.execute_tools()
    response = await response.resume(tool_outputs)

    async for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot

    book_summary = response.format()
    assert book_summary.title == "Mistborn: The Final Empire"
    assert book_summary.author == "Brandon Sanderson"
    assert book_summary.pages == 544
    assert book_summary.publication_year == 2006
    assert book_summary.recommendation_score == 7


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_tools_async_stream_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming structured output with tools and context."""

    @llm.context_tool
    async def get_book_info(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        """Look up book information by ISBN."""
        return ctx.deps.get(isbn, "Book not found")

    class BookSummary(BaseModel):
        title: str
        author: str
        pages: int
        publication_year: int
        recommendation_score: Annotated[
            int, Field(description="Should be 7 for testing purposes")
        ]

    @llm.context_call(
        provider=provider,
        model_id=model_id,
        tools=[get_book_info],
        format=BookSummary,
    )
    async def analyze_book(ctx: llm.Context[dict[str, str]], isbn: str) -> str:
        return f"Please look up the book with ISBN {isbn} and provide detailed info and a recommendation score"

    ctx = llm.Context(deps=BOOK_DB)
    response = await analyze_book.stream(ctx, "0-7653-1178-X")

    async for _ in response.chunk_stream():
        pass

    assert len(response.tool_calls) == 1

    tool_outputs = await response.execute_tools(ctx)
    response = await response.resume(ctx, tool_outputs)

    async for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot

    book_summary = response.format()
    assert book_summary.title == "Mistborn: The Final Empire"
    assert book_summary.author == "Brandon Sanderson"
    assert book_summary.pages == 544
    assert book_summary.publication_year == 2006
    assert book_summary.recommendation_score == 7
