"""Tests for validate() using retry semantics when resume encounters errors."""

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm

from .conftest import CONNECTION_ERROR
from .mock_provider import MockProvider

# --- Sync validate() with retry semantics ---


def test_validate_retries_on_connection_error_during_resume(
    mock_provider: MockProvider,
) -> None:
    """Test that validate() retries when resume encounters a ConnectionError."""

    class Person(BaseModel):
        name: str
        age: int

    # First response is invalid JSON (triggers parse error and resume)
    # Resume attempt 1 fails with ConnectionError, retry succeeds
    mock_provider.set_response_texts(["not valid json", '{"name": "Alice", "age": 30}'])

    retry_model = llm.retry(
        llm.Model("mock/primary"),
        max_retries=1,
    )

    response = retry_model.call("Get person", format=Person)
    assert response.text() == snapshot("not valid json")
    mock_provider.set_exceptions([CONNECTION_ERROR])

    # Parse fails, resume fails with ConnectionError, retry succeeds
    parsed, final_response = response.validate(max_retries=1)
    assert final_response.text() == snapshot('{"name": "Alice", "age": 30}')

    assert parsed is not None
    assert parsed.name == "Alice"
    assert parsed.age == 30
    # 1 initial + 1 failed resume (ConnectionError) + 1 successful retry
    assert mock_provider.call_count == 3


def test_validate_uses_fallback_when_resume_fails(
    mock_provider: MockProvider,
) -> None:
    """Test that validate() falls back to another model when resume fails on primary."""

    class Person(BaseModel):
        name: str
        age: int

    # First response is invalid JSON (triggers parse error and resume)
    # Resume on primary fails with ConnectionError, fallback succeeds
    mock_provider.set_response_texts(["not valid json", '{"name": "Bob", "age": 25}'])

    retry_model = llm.retry(
        llm.Model("mock/primary"),
        max_retries=0,  # No retries on primary, must fall back
        fallback_models=["mock/fallback"],
    )

    response = retry_model.call("Get person", format=Person)
    assert response.text() == snapshot("not valid json")
    mock_provider.set_exceptions([CONNECTION_ERROR])

    # Parse fails, resume on primary fails, fallback succeeds
    parsed, final_response = response.validate(max_retries=1)
    assert final_response.text() == snapshot('{"name": "Bob", "age": 25}')

    assert parsed is not None
    assert parsed.name == "Bob"
    assert parsed.age == 25
    # 1 initial + 1 failed resume on primary + 1 successful on fallback
    assert mock_provider.call_count == 3


# --- Async validate() with retry semantics ---


@pytest.mark.asyncio
async def test_async_validate_retries_on_connection_error_during_resume(
    mock_provider: MockProvider,
) -> None:
    """Test that async validate() retries when resume encounters a ConnectionError."""

    class Person(BaseModel):
        name: str
        age: int

    # First response is invalid JSON (triggers parse error and resume)
    # Resume attempt 1 fails with ConnectionError, retry succeeds
    mock_provider.set_response_texts(["not valid json", '{"name": "Carol", "age": 35}'])

    retry_model = llm.retry(
        llm.Model("mock/primary"),
        max_retries=1,
    )

    response = await retry_model.call_async("Get person", format=Person)
    assert response.text() == snapshot("not valid json")
    mock_provider.set_exceptions([CONNECTION_ERROR])

    # Parse fails, resume fails with ConnectionError, retry succeeds
    parsed, final_response = await response.validate(max_retries=1)
    assert final_response.text() == snapshot('{"name": "Carol", "age": 35}')

    assert parsed is not None
    assert parsed.name == "Carol"
    assert parsed.age == 35
    # 1 initial + 1 failed resume (ConnectionError) + 1 successful retry
    assert mock_provider.call_count == 3


@pytest.mark.asyncio
async def test_async_validate_uses_fallback_when_resume_fails(
    mock_provider: MockProvider,
) -> None:
    """Test that async validate() falls back to another model when resume fails on primary."""

    class Person(BaseModel):
        name: str
        age: int

    # First response is invalid JSON (triggers parse error and resume)
    # Resume on primary fails with ConnectionError, fallback succeeds
    mock_provider.set_response_texts(["not valid json", '{"name": "Dave", "age": 40}'])

    retry_model = llm.retry(
        llm.Model("mock/primary"),
        max_retries=0,  # No retries on primary, must fall back
        fallback_models=["mock/fallback"],
    )

    response = await retry_model.call_async("Get person", format=Person)
    assert response.text() == snapshot("not valid json")
    mock_provider.set_exceptions([CONNECTION_ERROR])

    # Parse fails, resume on primary fails, fallback succeeds
    parsed, final_response = await response.validate(max_retries=1)
    assert final_response.text() == snapshot('{"name": "Dave", "age": 40}')

    assert parsed is not None
    assert parsed.name == "Dave"
    assert parsed.age == 40
    # 1 initial + 1 failed resume on primary + 1 successful on fallback
    assert mock_provider.call_count == 3
