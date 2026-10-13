"""Tests for OpenAIResponsesProvider"""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest
from openai import RateLimitError as OpenAIRateLimitError
from openai.types.responses import Response
from openai.types.responses.response_stream_event import ResponseStreamEvent

from mirascope import llm
from mirascope.llm.providers.openai.provider import OpenAIProvider
from mirascope.llm.providers.openai.responses._utils.decode import decode_response


def test_stream_rate_limit_error() -> None:
    """Test that OpenAI RateLimitError is caught and re-wrapped during streaming calls."""
    model = llm.Model("openai/gpt-4o:responses")
    provider = model.provider
    assert isinstance(provider, OpenAIProvider)
    responses_provider = provider._responses_provider  # pyright: ignore[reportPrivateUsage]

    # Create a mock stream that raises RateLimitError
    def mock_stream() -> Iterator[ResponseStreamEvent]:
        raise OpenAIRateLimitError(
            "Rate limit exceeded", response=MagicMock(status_code=429), body=None
        )
        yield  # pragma: no cover

    # Patch the client to return our mock stream
    with patch.object(
        responses_provider.client.responses,
        "create",
        return_value=mock_stream(),
    ):
        # Try to stream and expect RateLimitError
        response = model.stream("test")

        with pytest.raises(llm.RateLimitError) as exc_info:
            response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, OpenAIRateLimitError)


@pytest.mark.asyncio
async def test_async_stream_rate_limit_error() -> None:
    """Test that OpenAI RateLimitError is caught and re-wrapped during async streaming calls."""
    model = llm.Model("openai/gpt-4o:responses")
    provider = model.provider
    assert isinstance(provider, OpenAIProvider)
    responses_provider = provider._responses_provider  # pyright: ignore[reportPrivateUsage]

    # Create a mock async stream that raises RateLimitError
    class MockAsyncStream:
        def __aiter__(self) -> "MockAsyncStream":
            return self

        async def __anext__(self) -> ResponseStreamEvent:
            raise OpenAIRateLimitError(
                "Rate limit exceeded", response=MagicMock(status_code=429), body=None
            )

    # Create an async function that returns the mock stream
    async def create_mock_stream(**kwargs: object) -> MockAsyncStream:
        return MockAsyncStream()

    # Patch the async client to return our mock stream
    with patch.object(
        responses_provider.async_client.responses,
        "create",
        side_effect=create_mock_stream,
    ):
        # Try to stream and expect RateLimitError
        response = await model.stream_async("test")

        with pytest.raises(llm.RateLimitError) as exc_info:
            await response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, OpenAIRateLimitError)


def test_call_rate_limit_error() -> None:
    """Test that OpenAI RateLimitError is caught and re-wrapped during non-streaming calls."""
    model = llm.Model("openai/gpt-4o:responses")
    provider = model.provider
    assert isinstance(provider, OpenAIProvider)
    responses_provider = provider._responses_provider  # pyright: ignore[reportPrivateUsage]

    # Patch the client to raise RateLimitError
    with patch.object(
        responses_provider.client.responses,
        "create",
        side_effect=OpenAIRateLimitError(
            "Rate limit exceeded", response=MagicMock(status_code=429), body=None
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            model.call("test")

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, OpenAIRateLimitError)


@pytest.mark.asyncio
async def test_async_call_rate_limit_error() -> None:
    """Test that OpenAI RateLimitError is caught and re-wrapped during async non-streaming calls."""
    model = llm.Model("openai/gpt-4o:responses")
    provider = model.provider
    assert isinstance(provider, OpenAIProvider)
    responses_provider = provider._responses_provider  # pyright: ignore[reportPrivateUsage]

    # Patch the async client to raise RateLimitError
    with patch.object(
        responses_provider.async_client.responses,
        "create",
        side_effect=OpenAIRateLimitError(
            "Rate limit exceeded", response=MagicMock(status_code=429), body=None
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            await model.call_async("test")

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, OpenAIRateLimitError)


def test_decode_response_empty_tool_arguments() -> None:
    """Test that empty or whitespace tool arguments decode to '{}' in responses."""
    resp = Response.model_validate(
        {
            "id": "resp_1",
            "created_at": 1234567890,
            "model": "gpt-4o",
            "object": "response",
            "output": [
                {
                    "type": "function_call",
                    "call_id": "call_1",
                    "name": "no_args_tool",
                    "arguments": "",
                },
                {
                    "type": "function_call",
                    "call_id": "call_2",
                    "name": "whitespace_args_tool",
                    "arguments": "   ",
                },
                {
                    "type": "function_call",
                    "call_id": "call_3",
                    "name": "normal_args_tool",
                    "arguments": '{"x": 1}',
                },
            ],
            "status": "completed",
            "parallel_tool_calls": True,
            "tools": [],
            "tool_choice": "auto",
        }
    )
    assistant_message, _, _ = decode_response(
        resp, "openai/gpt-4o", "openai:responses", include_thoughts=False
    )
    assert assistant_message.content == [
        llm.ToolCall(id="call_1", name="no_args_tool", args="{}"),
        llm.ToolCall(id="call_2", name="whitespace_args_tool", args="{}"),
        llm.ToolCall(id="call_3", name="normal_args_tool", args='{"x": 1}'),
    ]
