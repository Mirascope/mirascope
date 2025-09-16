"""End-to-end tests for structured output."""

import pytest
from pydantic import BaseModel

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS, Snapshot
from tests.utils import response_snapshot_dict, stream_response_snapshot_dict

# ============= SYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_structured_output_sync(
    provider: llm.clients.Provider,
    model_id: llm.clients.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test synchronous structured output without context."""

    class Book(BaseModel):
        title: str
        author: str

    @llm.call(provider=provider, model_id=model_id, format=Book)
    def recommend_book(author: str) -> str:
        return f"Please recommend the most popular book by {author}"

    response = recommend_book("Patrick Rothfuss")
    assert response_snapshot_dict(response) == snapshot

    book = response.format()
    assert book.author == "Patrick Rothfuss"
    assert book.title == "The Name of the Wind"


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_structured_output_sync_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test synchronous structured output with context."""

    class Book(BaseModel):
        title: str
        author: str

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=Book,
    )
    def recommend_book(ctx: llm.Context[str]) -> str:
        return f"Please recommend the most popular book by {ctx.deps}"

    ctx = llm.Context(deps="Patrick Rothfuss")
    response = recommend_book(ctx)
    assert response_snapshot_dict(response) == snapshot

    book = response.format()
    assert book.author == "Patrick Rothfuss"
    assert book.title == "The Name of the Wind"


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_async(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous structured output without context."""

    class Book(BaseModel):
        title: str
        author: str

    @llm.call(provider=provider, model_id=model_id, format=Book)
    async def recommend_book(author: str) -> str:
        return f"Please recommend the most popular book by {author}"

    response = await recommend_book("Patrick Rothfuss")
    assert response_snapshot_dict(response) == snapshot

    book = response.format()
    assert book.author == "Patrick Rothfuss"
    assert book.title == "The Name of the Wind"


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_async_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous structured output with context."""

    class Book(BaseModel):
        title: str
        author: str

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=Book,
    )
    async def recommend_book(ctx: llm.Context[str]) -> str:
        return f"Please recommend the most popular book by {ctx.deps}"

    ctx = llm.Context(deps="Patrick Rothfuss")
    response = await recommend_book(ctx)
    assert response_snapshot_dict(response) == snapshot

    book = response.format()
    assert book.author == "Patrick Rothfuss"
    assert book.title == "The Name of the Wind"


# ============= STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_structured_output_stream(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming structured output without context."""

    class Book(BaseModel):
        title: str
        author: str

    @llm.call(provider=provider, model_id=model_id, format=Book)
    def recommend_book(author: str) -> str:
        return f"Please recommend the most popular book by {author}"

    response = recommend_book.stream("Patrick Rothfuss")

    for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot

    book = response.format()
    assert book.author == "Patrick Rothfuss"
    assert book.title == "The Name of the Wind"


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_structured_output_stream_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming structured output with context."""

    class Book(BaseModel):
        title: str
        author: str

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=Book,
    )
    def recommend_book(ctx: llm.Context[str]) -> str:
        return f"Please recommend the most popular book by {ctx.deps}"

    ctx = llm.Context(deps="Patrick Rothfuss")
    response = recommend_book.stream(ctx)

    for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot

    book = response.format()
    assert book.author == "Patrick Rothfuss"
    assert book.title == "The Name of the Wind"


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_async_stream(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming structured output without context."""

    class Book(BaseModel):
        title: str
        author: str

    @llm.call(provider=provider, model_id=model_id, format=Book)
    async def recommend_book(author: str) -> str:
        return f"Please recommend the most popular book by {author}"

    response = await recommend_book.stream("Patrick Rothfuss")

    async for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot

    book = response.format()
    assert book.author == "Patrick Rothfuss"
    assert book.title == "The Name of the Wind"


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_structured_output_async_stream_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming structured output with context."""

    class Book(BaseModel):
        title: str
        author: str

    @llm.call(
        provider=provider,
        model_id=model_id,
        format=Book,
    )
    async def recommend_book(ctx: llm.Context[str]) -> str:
        return f"Please recommend the most popular book by {ctx.deps}"

    ctx = llm.Context(deps="Patrick Rothfuss")
    response = await recommend_book.stream(ctx)

    async for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot

    book = response.format()
    assert book.author == "Patrick Rothfuss"
    assert book.title == "The Name of the Wind"
