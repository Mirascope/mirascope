"""Stream creation failures share the request's existing retry budget."""

from typing import Literal

import pytest

from mirascope import llm

from .conftest import CONNECTION_ERROR, RATE_LIMIT_ERROR, SERVER_ERROR
from .mock_provider import MockProvider

Entry = Literal["stream", "resume", "context", "context_resume"]
ENTRIES: tuple[Entry, ...] = ("stream", "resume", "context", "context_resume")


def start_stream(
    model: llm.RetryModel,
    entry: Entry,
    provider: MockProvider,
    failures: list[BaseException],
) -> llm.RetryStreamResponse[None] | llm.ContextRetryStreamResponse[None, None]:
    """Prepare resume inputs before enabling failures on the new request."""
    ctx = llm.Context(deps=None)
    previous = llm.Model("mock/test-model").stream("Previous")
    context_previous = llm.Model("mock/test-model").context_stream("Previous", ctx=ctx)
    provider.set_stream_creation_exceptions(failures)
    if entry == "stream":
        return model.stream("Hello")
    if entry == "context":
        return model.context_stream("Hello", ctx=ctx)
    if entry == "resume":
        return model.resume_stream(response=previous, content="Hello")
    return model.context_resume_stream(
        ctx=ctx, response=context_previous, content="Hello"
    )


async def start_stream_async(
    model: llm.RetryModel,
    entry: Entry,
    provider: MockProvider,
    failures: list[BaseException],
) -> (
    llm.AsyncRetryStreamResponse[None] | llm.AsyncContextRetryStreamResponse[None, None]
):
    """Prepare resume inputs before enabling failures on the new async request."""
    ctx = llm.Context(deps=None)
    previous = await llm.Model("mock/test-model").stream_async("Previous")
    context_previous = await llm.Model("mock/test-model").context_stream_async(
        "Previous", ctx=ctx
    )
    provider.set_stream_creation_exceptions(failures)
    if entry == "stream":
        return await model.stream_async("Hello")
    if entry == "context":
        return await model.context_stream_async("Hello", ctx=ctx)
    if entry == "resume":
        return await model.resume_stream_async(response=previous, content="Hello")
    return await model.context_resume_stream_async(
        ctx=ctx, response=context_previous, content="Hello"
    )


@pytest.mark.parametrize("entry", ENTRIES)
def test_creation_retry_preserves_metadata(
    mock_provider: MockProvider, entry: Entry
) -> None:
    """A creation failure retries silently before any content was emitted."""
    model = llm.retry_model("mock/test-model", max_retries=2)
    response = start_stream(
        model, entry, mock_provider, [CONNECTION_ERROR, RATE_LIMIT_ERROR]
    )
    assert "".join(response.text_stream()) == "mock response\n"
    assert [failure.exception for failure in response.retry_failures] == [
        CONNECTION_ERROR,
        RATE_LIMIT_ERROR,
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("entry", ENTRIES)
async def test_async_creation_retry_preserves_metadata(
    mock_provider: MockProvider, entry: Entry
) -> None:
    """Async creation also returns both failed attempts in retry metadata."""
    model = llm.retry_model("mock/test-model", max_retries=2)
    response = await start_stream_async(
        model, entry, mock_provider, [CONNECTION_ERROR, RATE_LIMIT_ERROR]
    )
    assert (
        "".join([chunk async for chunk in response.text_stream()]) == "mock response\n"
    )
    assert [failure.exception for failure in response.retry_failures] == [
        CONNECTION_ERROR,
        RATE_LIMIT_ERROR,
    ]


@pytest.mark.parametrize("entry", ENTRIES)
def test_creation_and_iteration_share_budget(
    mock_provider: MockProvider, entry: Entry
) -> None:
    """A creation retry must not restart the budget for iteration failures."""
    model = llm.retry_model("mock/test-model", max_retries=1)
    mock_provider.set_stream_exceptions([SERVER_ERROR])
    response = start_stream(model, entry, mock_provider, [CONNECTION_ERROR])
    with pytest.raises(llm.RetriesExhausted) as exc:
        list(response.text_stream())
    assert [failure.exception for failure in exc.value.failures] == [
        CONNECTION_ERROR,
        SERVER_ERROR,
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("entry", ENTRIES)
async def test_async_creation_and_iteration_share_budget(
    mock_provider: MockProvider, entry: Entry
) -> None:
    """Async iteration uses only the variants left after creation succeeds."""
    model = llm.retry_model("mock/test-model", max_retries=1)
    mock_provider.set_stream_exceptions([SERVER_ERROR])
    response = await start_stream_async(model, entry, mock_provider, [CONNECTION_ERROR])
    with pytest.raises(llm.RetriesExhausted) as exc:
        _ = [chunk async for chunk in response.text_stream()]
    assert [failure.exception for failure in exc.value.failures] == [
        CONNECTION_ERROR,
        SERVER_ERROR,
    ]


@pytest.mark.parametrize("entry", ENTRIES)
def test_creation_exhausts_configured_attempts(
    mock_provider: MockProvider, entry: Entry
) -> None:
    """Creation failures report every attempt when no stream can be opened."""
    model = llm.retry_model("mock/test-model", max_retries=1)
    with pytest.raises(llm.RetriesExhausted) as exc:
        start_stream(model, entry, mock_provider, [CONNECTION_ERROR, RATE_LIMIT_ERROR])
    assert [failure.exception for failure in exc.value.failures] == [
        CONNECTION_ERROR,
        RATE_LIMIT_ERROR,
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("entry", ENTRIES)
async def test_async_creation_exhausts_configured_attempts(
    mock_provider: MockProvider, entry: Entry
) -> None:
    """Async creation failures preserve the configured attempt limit."""
    model = llm.retry_model("mock/test-model", max_retries=1)
    with pytest.raises(llm.RetriesExhausted) as exc:
        await start_stream_async(
            model, entry, mock_provider, [CONNECTION_ERROR, RATE_LIMIT_ERROR]
        )
    assert [failure.exception for failure in exc.value.failures] == [
        CONNECTION_ERROR,
        RATE_LIMIT_ERROR,
    ]


@pytest.mark.parametrize("entry", ENTRIES)
def test_creation_uses_fallback(mock_provider: MockProvider, entry: Entry) -> None:
    """A fallback selected during creation remains active on the response."""
    model = llm.retry_model(
        "mock/test-model", max_retries=0, fallback_models=["mock/fallback"]
    )
    response = start_stream(model, entry, mock_provider, [CONNECTION_ERROR])
    assert "".join(response.text_stream()) == "mock response\n"
    assert response.model.model_id == "mock/fallback"
    assert response.retry_failures[0].model.model_id == "mock/test-model"


@pytest.mark.asyncio
@pytest.mark.parametrize("entry", ENTRIES)
async def test_async_creation_uses_fallback(
    mock_provider: MockProvider, entry: Entry
) -> None:
    """Async creation records the primary failure and returns its fallback."""
    model = llm.retry_model(
        "mock/test-model", max_retries=0, fallback_models=["mock/fallback"]
    )
    response = await start_stream_async(model, entry, mock_provider, [CONNECTION_ERROR])
    assert (
        "".join([chunk async for chunk in response.text_stream()]) == "mock response\n"
    )
    assert response.model.model_id == "mock/fallback"
    assert response.retry_failures[0].model.model_id == "mock/test-model"


@pytest.mark.parametrize("entry", ENTRIES)
def test_creation_does_not_retry_other_errors(
    mock_provider: MockProvider, entry: Entry
) -> None:
    """Errors outside retry_on surface immediately without becoming exhaustion."""
    error = ValueError("not retryable")
    with pytest.raises(ValueError, match="not retryable"):
        start_stream(llm.retry_model("mock/test-model"), entry, mock_provider, [error])


@pytest.mark.asyncio
@pytest.mark.parametrize("entry", ENTRIES)
async def test_async_creation_does_not_retry_other_errors(
    mock_provider: MockProvider, entry: Entry
) -> None:
    """Async creation leaves errors outside retry_on untouched."""
    error = ValueError("not retryable")
    with pytest.raises(ValueError, match="not retryable"):
        await start_stream_async(
            llm.retry_model("mock/test-model"), entry, mock_provider, [error]
        )
