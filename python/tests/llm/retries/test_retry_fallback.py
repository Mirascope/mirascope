"""Tests for fallback model functionality and retry failure tracking."""

import pytest

from mirascope import llm

from .conftest import CONNECTION_ERROR, RATE_LIMIT_ERROR
from .mock_provider import MockProvider

# --- Fallback model tests ---


def test_fallback_with_model_id_inherits_params(mock_provider: MockProvider) -> None:
    """Test that ModelId fallbacks inherit params from primary model."""
    model = llm.Model("mock/primary", temperature=0.5)
    retry_model = llm.retry(model, max_retries=0, fallback_models=["mock/fallback"])

    # Access internal models to verify params inheritance
    models = retry_model._models  # pyright: ignore[reportPrivateUsage]
    assert len(models) == 2
    assert models[0].model_id == "mock/primary"
    assert models[1].model_id == "mock/fallback"
    assert models[1].params.get("temperature") == 0.5


def test_fallback_with_model_instance_uses_own_params(
    mock_provider: MockProvider,
) -> None:
    """Test that Model instance fallbacks use their own params."""
    primary = llm.Model("mock/primary", temperature=0.5)
    fallback = llm.Model("mock/fallback", temperature=0.9)
    retry_model = llm.retry(primary, max_retries=0, fallback_models=[fallback])

    models = retry_model._models  # pyright: ignore[reportPrivateUsage]
    assert len(models) == 2
    assert models[0].params.get("temperature") == 0.5
    assert models[1].params.get("temperature") == 0.9


def test_fallback_strips_retry_model_wrapper(mock_provider: MockProvider) -> None:
    """Test that RetryModel fallbacks are stripped to plain Model."""
    primary = llm.Model("mock/primary")
    nested_retry = llm.retry(
        llm.Model("mock/fallback", temperature=0.7),
        max_retries=5,
        fallback_models=["mock/nested-fallback"],
    )
    retry_model = llm.retry(primary, max_retries=0, fallback_models=[nested_retry])

    models = retry_model._models  # pyright: ignore[reportPrivateUsage]
    assert len(models) == 2
    # The nested RetryModel should be stripped to a plain Model
    assert type(models[1]) is llm.Model
    assert models[1].model_id == "mock/fallback"
    assert models[1].params.get("temperature") == 0.7


def test_fallback_model_tried_after_primary_exhausted(
    mock_provider: MockProvider,
) -> None:
    """Test that fallback model is tried when primary exhausts retries."""
    # Primary model will fail, fallback will succeed
    mock_provider.set_exceptions([CONNECTION_ERROR])

    primary = llm.Model("mock/primary")
    retry_model = llm.retry(primary, max_retries=0, fallback_models=["mock/fallback"])

    response = retry_model.call("Hello")

    # Should have succeeded on fallback
    assert response.model_id == "mock/fallback"
    assert len(response.retry_failures) == 1


def test_fallback_model_gets_own_retry_budget(mock_provider: MockProvider) -> None:
    """Test that each fallback model gets its own full retry budget."""
    # Primary fails twice, fallback fails once then succeeds
    mock_provider.set_exceptions(
        [
            CONNECTION_ERROR,  # primary attempt 1
            CONNECTION_ERROR,  # primary attempt 2 (retry)
            RATE_LIMIT_ERROR,  # fallback attempt 1
        ]
    )

    primary = llm.Model("mock/primary")
    retry_model = llm.retry(primary, max_retries=1, fallback_models=["mock/fallback"])

    response = retry_model.call("Hello")

    # Should have succeeded on fallback's second attempt
    assert response.model_id == "mock/fallback"
    assert len(response.retry_failures) == 3  # 2 primary + 1 fallback failures


def test_response_model_property_returns_retry_model_with_successful_active(
    mock_provider: MockProvider,
) -> None:
    """Test that response.model returns RetryModel with successful model as active."""
    mock_provider.set_exceptions([CONNECTION_ERROR])

    primary = llm.Model("mock/primary")
    retry_model = llm.retry(primary, max_retries=0, fallback_models=["mock/fallback"])

    response = retry_model.call("Hello")

    # response.model should be a RetryModel with fallback as active
    assert isinstance(response.model, llm.retries.RetryModel)
    assert response.model.model_id == "mock/fallback"
    assert response.model.model_id == response.model_id


# --- Retry failure tracking tests ---


def test_retry_failures_track_model_and_exception(mock_provider: MockProvider) -> None:
    """Test that retry_failures tracks both model and exception."""
    mock_provider.set_exceptions([CONNECTION_ERROR])

    model = llm.Model("mock/test-model")
    retry_model = llm.retry(model, max_retries=1)

    response = retry_model.call("Hello")

    assert len(response.retry_failures) == 1
    assert response.retry_failures[0].model.model_id == "mock/test-model"
    assert response.retry_failures[0].exception is CONNECTION_ERROR


# --- Stream fallback model tests ---


def test_stream_fallback_model_tried_after_primary_exhausted(
    mock_provider: MockProvider,
) -> None:
    """Test that fallback model is tried when primary exhausts retries during streaming."""
    # Primary model will fail mid-stream, fallback will succeed
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    primary = llm.Model("mock/primary")
    retry_model = llm.retry(primary, max_retries=0, fallback_models=["mock/fallback"])

    response = retry_model.stream("Hello")

    # First iteration fails, triggers StreamRestarted
    with pytest.raises(llm.StreamRestarted) as exc_info:
        list(response.chunk_stream())

    assert exc_info.value.attempt == 1

    # After restart, should use fallback model
    assert response.model.model_id == "mock/fallback"
    assert len(response.retry_failures) == 1
    assert response.retry_failures[0].model.model_id == "mock/primary"

    # Second iteration succeeds on fallback
    chunks = list(response.chunk_stream())
    assert len(chunks) > 0


def test_stream_fallback_model_gets_own_retry_budget(
    mock_provider: MockProvider,
) -> None:
    """Test that each fallback model gets its own full retry budget during streaming."""
    # Primary fails twice (exhaust budget), fallback fails once then succeeds
    mock_provider.set_stream_exceptions(
        [
            CONNECTION_ERROR,  # primary attempt 1
            CONNECTION_ERROR,  # primary attempt 2 (retry)
            RATE_LIMIT_ERROR,  # fallback attempt 1
        ]
    )

    primary = llm.Model("mock/primary")
    retry_model = llm.retry(primary, max_retries=1, fallback_models=["mock/fallback"])

    response = retry_model.stream("Hello")

    # First iteration: primary attempt 1 fails
    with pytest.raises(llm.StreamRestarted) as exc_info:
        list(response.chunk_stream())
    assert exc_info.value.attempt == 1
    assert response.model.model_id == "mock/primary"  # Still on primary (has retries)

    # Second iteration: primary attempt 2 (retry) fails, moves to fallback
    with pytest.raises(llm.StreamRestarted) as exc_info:
        list(response.chunk_stream())
    assert exc_info.value.attempt == 2
    assert response.model.model_id == "mock/fallback"  # Now on fallback

    # Third iteration: fallback attempt 1 fails
    with pytest.raises(llm.StreamRestarted) as exc_info:
        list(response.chunk_stream())
    assert exc_info.value.attempt == 3
    assert response.model.model_id == "mock/fallback"  # Still on fallback (has retries)

    # Fourth iteration: fallback attempt 2 succeeds
    chunks = list(response.chunk_stream())
    assert len(chunks) > 0
    assert len(response.retry_failures) == 3


def test_stream_raises_after_all_fallbacks_exhausted(
    mock_provider: MockProvider,
) -> None:
    """Test that RetriesExhausted is raised when all fallback models are exhausted."""
    # Both models fail all attempts
    mock_provider.set_stream_exceptions(
        [
            CONNECTION_ERROR,  # primary
            RATE_LIMIT_ERROR,  # fallback
        ]
    )

    primary = llm.Model("mock/primary")
    retry_model = llm.retry(primary, max_retries=0, fallback_models=["mock/fallback"])

    response = retry_model.stream("Hello")

    # First: primary fails
    with pytest.raises(llm.StreamRestarted):
        list(response.chunk_stream())

    # Second: fallback fails, no more models -> raises RetriesExhausted
    with pytest.raises(llm.RetriesExhausted) as exc_info:
        list(response.chunk_stream())

    assert len(exc_info.value.failures) == 2
    assert isinstance(exc_info.value.failures[0].exception, llm.ConnectionError)
    assert isinstance(exc_info.value.failures[1].exception, llm.RateLimitError)


# --- Async stream fallback model tests ---


@pytest.mark.asyncio
async def test_stream_async_fallback_model_tried_after_primary_exhausted(
    mock_provider: MockProvider,
) -> None:
    """Test that fallback model is tried when primary exhausts retries during async streaming."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    primary = llm.Model("mock/primary")
    retry_model = llm.retry(primary, max_retries=0, fallback_models=["mock/fallback"])

    response = await retry_model.stream_async("Hello")

    # First iteration fails
    with pytest.raises(llm.StreamRestarted) as exc_info:
        async for _ in response.chunk_stream():
            pass
    assert exc_info.value.attempt == 1

    # After restart, should use fallback model
    assert response.model.model_id == "mock/fallback"
    assert len(response.retry_failures) == 1

    # Second iteration succeeds
    chunks = [chunk async for chunk in response.chunk_stream()]
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_stream_async_fallback_gets_own_retry_budget(
    mock_provider: MockProvider,
) -> None:
    """Test that each fallback model gets its own retry budget during async streaming."""
    mock_provider.set_stream_exceptions(
        [
            CONNECTION_ERROR,  # primary attempt 1
            CONNECTION_ERROR,  # primary attempt 2 (retry)
            RATE_LIMIT_ERROR,  # fallback attempt 1
        ]
    )

    primary = llm.Model("mock/primary")
    retry_model = llm.retry(primary, max_retries=1, fallback_models=["mock/fallback"])

    response = await retry_model.stream_async("Hello")

    # Exhaust primary's budget
    with pytest.raises(llm.StreamRestarted):
        async for _ in response.chunk_stream():
            pass
    with pytest.raises(llm.StreamRestarted):
        async for _ in response.chunk_stream():
            pass

    # Now on fallback
    assert response.model.model_id == "mock/fallback"

    # Fallback fails once
    with pytest.raises(llm.StreamRestarted):
        async for _ in response.chunk_stream():
            pass

    # Fallback succeeds on retry
    chunks = [chunk async for chunk in response.chunk_stream()]
    assert len(chunks) > 0
    assert len(response.retry_failures) == 3
