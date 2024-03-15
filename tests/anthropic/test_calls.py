"""Tests for `AnthropicCall`."""
from typing import AsyncContextManager, ContextManager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import ContentBlockDeltaEvent, Message
from pytest import FixtureRequest

from mirascope.anthropic.calls import AnthropicCall
from mirascope.anthropic.types import (
    AnthropicCallResponse,
    AnthropicCallResponseChunk,
)


@pytest.mark.parametrize(
    "call,expected_messages",
    [
        (
            "fixture_anthropic_test_call",
            [{"role": "user", "content": "This is a test prompt for Anthropic."}],
        ),
        (
            "fixture_anthropic_test_messages_call",
            [
                {"role": "system", "content": "System message"},
                {"role": "user", "content": "User message"},
            ],
        ),
    ],
)
def test_anthropic_call_messages(call: str, expected_messages, request: FixtureRequest):
    """Tests the prompt property."""
    prompt: AnthropicCall = request.getfixturevalue(call)
    assert prompt.messages() == expected_messages


@patch(
    "anthropic.resources.messages.Messages.create",
    new_callable=MagicMock,
)
def test_anthropic_call_call(
    mock_create: MagicMock,
    fixture_anthropic_test_messages_call: AnthropicCall,
    fixture_anthropic_message: Message,
):
    """Tests `AnthropicCall.call` returns the expected response when called."""
    mock_create.return_value = fixture_anthropic_message

    response = fixture_anthropic_test_messages_call.call()
    assert isinstance(response, AnthropicCallResponse)
    messages = fixture_anthropic_test_messages_call.messages()
    mock_create.assert_called_once_with(
        model=fixture_anthropic_test_messages_call.call_params.model,
        system=messages[0]["content"],
        messages=messages[1:],
        stream=False,
        temperature=0.3,
        max_tokens=fixture_anthropic_test_messages_call.call_params.max_tokens,
        timeout=fixture_anthropic_test_messages_call.call_params.timeout,
    )


@patch(
    "anthropic.resources.messages.AsyncMessages.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_anthropic_call_call_async(
    mock_create: AsyncMock,
    fixture_anthropic_test_messages_call: AnthropicCall,
    fixture_anthropic_message: Message,
):
    """Tests `AnthropicCall.call_async` returns the expected response when called."""
    mock_create.return_value = fixture_anthropic_message

    response = await fixture_anthropic_test_messages_call.call_async()
    assert isinstance(response, AnthropicCallResponse)
    messages = fixture_anthropic_test_messages_call.messages()
    mock_create.assert_called_once_with(
        model=fixture_anthropic_test_messages_call.call_params.model,
        system=messages[0]["content"],
        messages=messages[1:],
        stream=False,
        temperature=0.3,
        max_tokens=fixture_anthropic_test_messages_call.call_params.max_tokens,
        timeout=fixture_anthropic_test_messages_call.call_params.timeout,
    )


@patch(
    "anthropic.resources.messages.Messages.create",
    new_callable=MagicMock,
)
def test_anthropic_call_call_with_wrapper(
    mock_create: MagicMock, fixture_anthropic_test_call, fixture_anthropic_message
):
    """Tests `OpenAI` is created with a wrapper in `AnthropicPrompt.create`."""
    mock_create.return_value = fixture_anthropic_message
    wrapper = MagicMock()
    wrapper.return_value = Anthropic()

    fixture_anthropic_test_call.call_params.wrapper = wrapper
    fixture_anthropic_test_call.call()
    wrapper.assert_called_once()


@patch(
    "anthropic.resources.messages.AsyncMessages.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_anthropic_call_call_async_with_wrapper(
    mock_create: AsyncMock,
    fixture_anthropic_test_call: AnthropicCall,
    fixture_anthropic_message: Message,
):
    """Tests `OpenAI` is created with a wrapper in `AnthropicPrompt.create`."""
    mock_create.return_value = fixture_anthropic_message
    wrapper = MagicMock()
    wrapper.return_value = AsyncAnthropic()

    fixture_anthropic_test_call.call_params.wrapper_async = wrapper
    await fixture_anthropic_test_call.call_async()
    wrapper.assert_called_once()


@patch(
    "anthropic.resources.messages.Messages.stream",
    new_callable=MagicMock,
)
def test_anthropic_call_stream(
    mock_stream: MagicMock,
    fixture_anthropic_test_call: AnthropicCall,
    fixture_anthropic_message_chunk: ContentBlockDeltaEvent,
    fixture_anthropic_message_chunks: ContextManager[list],
):
    """Tests `AnthropicPrompt.stream` returns the expected response when called."""
    mock_stream.return_value = fixture_anthropic_message_chunks

    wrapper = MagicMock()
    wrapper.return_value = Anthropic()
    fixture_anthropic_test_call.call_params.wrapper = wrapper

    stream = fixture_anthropic_test_call.stream()
    for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
        assert chunk.chunk == fixture_anthropic_message_chunk
    wrapper.assert_called_once()
    mock_stream.assert_called_once_with(
        model=fixture_anthropic_test_call.call_params.model,
        messages=fixture_anthropic_test_call.messages(),
        temperature=0.3,
        max_tokens=fixture_anthropic_test_call.call_params.max_tokens,
        timeout=fixture_anthropic_test_call.call_params.timeout,
    )


@patch(
    "anthropic.resources.messages.AsyncMessages.stream",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_anthropic_call_stream_async(
    mock_stream: MagicMock,
    fixture_anthropic_test_call: AnthropicCall,
    fixture_anthropic_message_chunk: ContentBlockDeltaEvent,
    fixture_anthropic_async_message_chunks: AsyncContextManager[list],
):
    """Tests `AnthropicPrompt.stream` returns the expected response when called."""
    mock_stream.return_value = fixture_anthropic_async_message_chunks

    wrapper = MagicMock()
    wrapper.return_value = AsyncAnthropic()
    fixture_anthropic_test_call.call_params.wrapper_async = wrapper

    stream = fixture_anthropic_test_call.stream_async()
    async for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
        assert chunk.chunk == fixture_anthropic_message_chunk
    wrapper.assert_called_once()
    mock_stream.assert_called_once_with(
        model=fixture_anthropic_test_call.call_params.model,
        messages=fixture_anthropic_test_call.messages(),
        temperature=0.3,
        max_tokens=fixture_anthropic_test_call.call_params.max_tokens,
        timeout=fixture_anthropic_test_call.call_params.timeout,
    )
