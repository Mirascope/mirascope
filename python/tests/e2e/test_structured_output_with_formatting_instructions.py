"""End-to-end tests for structured output."""

import inspect

import pytest
from pydantic import BaseModel

from mirascope import llm
from tests.e2e.conftest import FORMATTING_MODES, PROVIDER_MODEL_ID_PAIRS, Snapshot
from tests.utils import (
    exception_snapshot_dict,
    response_snapshot_dict,
    stream_response_snapshot_dict,
)

# ============= SYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_with_formatting_instructions_sync(
    provider: llm.clients.Provider,
    model_id: llm.clients.ModelId,
    formatting_mode: llm.formatting.FormattingMode,
    snapshot: Snapshot,
) -> None:
    """Test synchronous structured output without context."""

    class Book(BaseModel):
        title: str
        author: str
        rating: int

        @classmethod
        def formatting_instructions(cls) -> str:
            return inspect.cleandoc("""
            Output a structured book as JSON in the format {title: str, author: str, rating: int}.
            The title should be in all caps, and the rating should always be the
            lucky number 7.
            """)

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=llm.format(Book, mode=formatting_mode),
    )
    def recommend_book(book: str) -> list[llm.Message]:
        return [
            llm.messages.system(f"Always recommend {book}."),
            llm.messages.user("Please recommend a book to me!"),
        ]

    try:
        response = recommend_book("The Name of the Wind")
        assert response_snapshot_dict(response) == snapshot

        book = response.format()
        assert book.author == "Patrick Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7
    except llm.FormattingModeNotSupportedError as e:
        assert exception_snapshot_dict(e) == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_with_formatting_instructions_sync_context(
    provider: llm.clients.Provider,
    model_id: llm.clients.ModelId,
    formatting_mode: llm.formatting.FormattingMode,
    snapshot: Snapshot,
) -> None:
    """Test synchronous structured output with context."""

    class Book(BaseModel):
        title: str
        author: str
        rating: int

        @classmethod
        def formatting_instructions(cls) -> str:
            return inspect.cleandoc("""
            Output a structured book as JSON in the format {title: str, author: str, rating: int}.
            The title should be in all caps, and the rating should always be the
            lucky number 7.
            """)

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=llm.format(Book, mode=formatting_mode),
    )
    def recommend_book(ctx: llm.Context[str]) -> list[llm.Message]:
        return [
            llm.messages.system(f"Always recommend {ctx.deps}."),
            llm.messages.user("Please recommend a book to me!"),
        ]

    ctx = llm.Context(deps="The Name of the Wind")
    try:
        response = recommend_book(ctx)
        assert response_snapshot_dict(response) == snapshot

        book = response.format()
        assert book.author == "Patrick Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7
    except llm.FormattingModeNotSupportedError as e:
        assert exception_snapshot_dict(e) == snapshot


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_formatting_instructions_async(
    provider: llm.clients.Provider,
    model_id: llm.clients.ModelId,
    formatting_mode: llm.formatting.FormattingMode,
    snapshot: Snapshot,
) -> None:
    """Test asynchronous structured output without context."""

    class Book(BaseModel):
        title: str
        author: str
        rating: int

        @classmethod
        def formatting_instructions(cls) -> str:
            return inspect.cleandoc("""
            Output a structured book as JSON in the format {title: str, author: str, rating: int}.
            The title should be in all caps, and the rating should always be the
            lucky number 7.
            """)

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=llm.format(Book, mode=formatting_mode),
    )
    async def recommend_book(book: str) -> list[llm.Message]:
        return [
            llm.messages.system(f"Always recommend {book}."),
            llm.messages.user("Please recommend a book to me!"),
        ]

    try:
        response = await recommend_book("The Name of the Wind")
        assert response_snapshot_dict(response) == snapshot

        book = response.format()
        assert book.author == "Patrick Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7
    except llm.FormattingModeNotSupportedError as e:
        assert exception_snapshot_dict(e) == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_formatting_instructions_async_context(
    provider: llm.clients.Provider,
    model_id: llm.clients.ModelId,
    formatting_mode: llm.formatting.FormattingMode,
    snapshot: Snapshot,
) -> None:
    """Test asynchronous structured output with context."""

    class Book(BaseModel):
        title: str
        author: str
        rating: int

        @classmethod
        def formatting_instructions(cls) -> str:
            return inspect.cleandoc("""
            Output a structured book as JSON in the format {title: str, author: str, rating: int}.
            The title should be in all caps, and the rating should always be the
            lucky number 7.
            """)

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=llm.format(Book, mode=formatting_mode),
    )
    async def recommend_book(ctx: llm.Context[str]) -> list[llm.Message]:
        return [
            llm.messages.system(f"Always recommend {ctx.deps}."),
            llm.messages.user("Please recommend a book to me!"),
        ]

    ctx = llm.Context(deps="The Name of the Wind")
    try:
        response = await recommend_book(ctx)
        assert response_snapshot_dict(response) == snapshot

        book = response.format()
        assert book.author == "Patrick Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7
    except llm.FormattingModeNotSupportedError as e:
        assert exception_snapshot_dict(e) == snapshot


# ============= STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_with_formatting_instructions_stream(
    provider: llm.clients.Provider,
    model_id: llm.clients.ModelId,
    formatting_mode: llm.formatting.FormattingMode,
    snapshot: Snapshot,
) -> None:
    """Test streaming structured output without context."""

    class Book(BaseModel):
        title: str
        author: str
        rating: int

        @classmethod
        def formatting_instructions(cls) -> str:
            return inspect.cleandoc("""
            Output a structured book as JSON in the format {title: str, author: str, rating: int}.
            The title should be in all caps, and the rating should always be the
            lucky number 7.
            """)

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=llm.format(Book, mode=formatting_mode),
    )
    def recommend_book(book: str) -> list[llm.Message]:
        return [
            llm.messages.system(f"Always recommend {book}."),
            llm.messages.user("Please recommend a book to me!"),
        ]

    try:
        response = recommend_book.stream("The Name of the Wind")
        for _ in response.chunk_stream():
            pass

        assert stream_response_snapshot_dict(response) == snapshot

        book = response.format()
        assert book.author == "Patrick Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7
    except llm.FormattingModeNotSupportedError as e:
        assert exception_snapshot_dict(e) == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_with_formatting_instructions_stream_context(
    provider: llm.clients.Provider,
    model_id: llm.clients.ModelId,
    formatting_mode: llm.formatting.FormattingMode,
    snapshot: Snapshot,
) -> None:
    """Test streaming structured output with context."""

    class Book(BaseModel):
        title: str
        author: str
        rating: int

        @classmethod
        def formatting_instructions(cls) -> str:
            return inspect.cleandoc("""
            Output a structured book as JSON in the format {title: str, author: str, rating: int}.
            The title should be in all caps, and the rating should always be the
            lucky number 7.
            """)

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=llm.format(Book, mode=formatting_mode),
    )
    def recommend_book(ctx: llm.Context[str]) -> list[llm.Message]:
        return [
            llm.messages.system(f"Always recommend {ctx.deps}."),
            llm.messages.user("Please recommend a book to me!"),
        ]

    ctx = llm.Context(deps="The Name of the Wind")
    try:
        response = recommend_book.stream(ctx)
        for _ in response.chunk_stream():
            pass

        assert stream_response_snapshot_dict(response) == snapshot

        book = response.format()
        assert book.author == "Patrick Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7
    except llm.FormattingModeNotSupportedError as e:
        assert exception_snapshot_dict(e) == snapshot


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_formatting_instructions_async_stream(
    provider: llm.clients.Provider,
    model_id: llm.clients.ModelId,
    formatting_mode: llm.formatting.FormattingMode,
    snapshot: Snapshot,
) -> None:
    """Test async streaming structured output without context."""

    class Book(BaseModel):
        title: str
        author: str
        rating: int

        @classmethod
        def formatting_instructions(cls) -> str:
            return inspect.cleandoc("""
            Output a structured book as JSON in the format {title: str, author: str, rating: int}.
            The title should be in all caps, and the rating should always be the
            lucky number 7.
            """)

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=llm.format(Book, mode=formatting_mode),
    )
    async def recommend_book(book: str) -> list[llm.Message]:
        return [
            llm.messages.system(f"Always recommend {book}."),
            llm.messages.user("Please recommend a book to me!"),
        ]

    try:
        response = await recommend_book.stream("The Name of the Wind")
        async for _ in response.chunk_stream():
            pass

        assert stream_response_snapshot_dict(response) == snapshot

        book = response.format()
        assert book.author == "Patrick Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7
    except llm.FormattingModeNotSupportedError as e:
        assert exception_snapshot_dict(e) == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_with_formatting_instructions_async_stream_context(
    provider: llm.clients.Provider,
    model_id: llm.clients.ModelId,
    formatting_mode: llm.formatting.FormattingMode,
    snapshot: Snapshot,
) -> None:
    """Test async streaming structured output with context."""

    class Book(BaseModel):
        title: str
        author: str
        rating: int

        @classmethod
        def formatting_instructions(cls) -> str:
            return inspect.cleandoc("""
            Output a structured book as JSON in the format {title: str, author: str, rating: int}.
            The title should be in all caps, and the rating should always be the
            lucky number 7.
            """)

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=llm.format(Book, mode=formatting_mode),
    )
    async def recommend_book(ctx: llm.Context[str]) -> list[llm.Message]:
        return [
            llm.messages.system(f"Always recommend {ctx.deps}."),
            llm.messages.user("Please recommend a book to me!"),
        ]

    ctx = llm.Context(deps="The Name of the Wind")
    try:
        response = await recommend_book.stream(ctx)
        async for _ in response.chunk_stream():
            pass

        assert stream_response_snapshot_dict(response) == snapshot

        book = response.format()
        assert book.author == "Patrick Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7
    except llm.FormattingModeNotSupportedError as e:
        assert exception_snapshot_dict(e) == snapshot
