"""Tests for mirascope anthropic prompt."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic import Anthropic, AsyncAnthropic

from mirascope.anthropic.prompt import AnthropicPrompt
from mirascope.anthropic.types import (
    AnthropicCompletion,
    AnthropicCompletionChunk,
)


@pytest.mark.parametrize(
    "prompt,expected_messages",
    [
        (
            "fixture_anthropic_test_prompt",
            [{"role": "user", "content": "This is a test prompt for Anthropic."}],
        ),
        (
            "fixture_anthropic_test_messages_prompt",
            [
                {"role": "user", "content": "User message"},
                {"role": "assistant", "content": "System message"},
                {"role": "user", "content": "User message"},
            ],
        ),
    ],
)
def test_anthropic_prompt_messages(prompt, expected_messages, request):
    """Tests the prompt property."""
    prompt = request.getfixturevalue(prompt)
    assert prompt.messages == expected_messages


def test_anthropic_prompt_bad_role():
    """Tests that messages raises a ValueError when given a bad role."""

    class MyPrompt(AnthropicPrompt):
        """
        BAD:
        Not a real role
        """

    with pytest.raises(ValueError):
        MyPrompt().messages


@patch(
    "anthropic.resources.messages.Messages.create",
    new_callable=MagicMock,
)
def test_anthropic_prompt_create(
    mock_create, fixture_anthropic_test_prompt, fixture_anthropic_message
):
    """Tests `AnthropicPrompt.create` returns the expected response when called."""
    mock_create.return_value = fixture_anthropic_message

    completion = fixture_anthropic_test_prompt.create()
    assert isinstance(completion, AnthropicCompletion)
    mock_create.assert_called_once_with(
        model=fixture_anthropic_test_prompt.call_params.model,
        messages=fixture_anthropic_test_prompt.messages,
        stream=False,
        temperature=0.3,
        max_tokens=fixture_anthropic_test_prompt.call_params.max_tokens,
        timeout=fixture_anthropic_test_prompt.call_params.timeout,
    )


@patch(
    "anthropic.resources.messages.AsyncMessages.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_anthropic_prompt_async_create(
    mock_create, fixture_anthropic_test_prompt, fixture_anthropic_message
):
    """Tests `AnthropicPrompt.async_create` returns the expected response when called."""
    mock_create.return_value = fixture_anthropic_message

    completion = await fixture_anthropic_test_prompt.async_create()
    assert isinstance(completion, AnthropicCompletion)
    mock_create.assert_called_once_with(
        model=fixture_anthropic_test_prompt.call_params.model,
        messages=fixture_anthropic_test_prompt.messages,
        stream=False,
        temperature=0.3,
        max_tokens=fixture_anthropic_test_prompt.call_params.max_tokens,
        timeout=fixture_anthropic_test_prompt.call_params.timeout,
    )


@patch(
    "anthropic.resources.messages.Messages.create",
    new_callable=MagicMock,
)
def test_anthropic_prompt_create_with_wrapper(
    mock_create, fixture_anthropic_test_prompt, fixture_anthropic_message
):
    """Tests `OpenAI` is created with a wrapper in `AnthropicPrompt.create`."""
    mock_create.return_value = fixture_anthropic_message
    wrapper = MagicMock()
    wrapper.return_value = Anthropic()

    fixture_anthropic_test_prompt.call_params.wrapper = wrapper
    fixture_anthropic_test_prompt.create()
    wrapper.assert_called_once()


@patch(
    "anthropic.resources.messages.AsyncMessages.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_anthropic_prompt_async_create_with_wrapper(
    mock_create, fixture_anthropic_test_prompt, fixture_anthropic_message
):
    """Tests `OpenAI` is created with a wrapper in `AnthropicPrompt.async_create`."""
    mock_create.return_value = fixture_anthropic_message
    wrapper = MagicMock()
    wrapper.return_value = AsyncAnthropic()

    fixture_anthropic_test_prompt.call_params.async_wrapper = wrapper
    await fixture_anthropic_test_prompt.async_create()
    wrapper.assert_called_once()


@patch(
    "anthropic.resources.messages.Messages.stream",
    new_callable=MagicMock,
)
def test_anthropic_prompt_stream(
    mock_stream,
    fixture_anthropic_test_prompt,
    fixture_anthropic_message_chunk,
    fixture_anthropic_message_chunks,
):
    """Tests `AnthropicPrompt.stream` returns the expected response when called."""
    mock_stream.return_value = fixture_anthropic_message_chunks

    stream = fixture_anthropic_test_prompt.stream()
    for chunk in stream:
        assert isinstance(chunk, AnthropicCompletionChunk)
        assert chunk.chunk == fixture_anthropic_message_chunk
    mock_stream.assert_called_once_with(
        model=fixture_anthropic_test_prompt.call_params.model,
        messages=fixture_anthropic_test_prompt.messages,
        temperature=0.3,
        max_tokens=fixture_anthropic_test_prompt.call_params.max_tokens,
        timeout=fixture_anthropic_test_prompt.call_params.timeout,
    )


@patch(
    "anthropic.resources.messages.AsyncMessages.stream",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_anthropic_prompt_async_stream(
    mock_stream,
    fixture_anthropic_test_prompt,
    fixture_anthropic_message_chunk,
    fixture_anthropic_async_message_chunks,
):
    """Tests `AnthropicPrompt.async_stream` returns the expected response when called."""
    mock_stream.return_value = fixture_anthropic_async_message_chunks

    stream = fixture_anthropic_test_prompt.async_stream()
    async for chunk in stream:
        assert isinstance(chunk, AnthropicCompletionChunk)
        assert chunk.chunk == fixture_anthropic_message_chunk
    mock_stream.assert_called_once_with(
        model=fixture_anthropic_test_prompt.call_params.model,
        messages=fixture_anthropic_test_prompt.messages,
        temperature=0.3,
        max_tokens=fixture_anthropic_test_prompt.call_params.max_tokens,
        timeout=fixture_anthropic_test_prompt.call_params.timeout,
    )


@patch(
    "anthropic.resources.messages.Messages.stream",
    new_callable=MagicMock,
)
def test_anthropic_prompt_stream_with_wrapper(
    mock_stream,
    fixture_anthropic_test_prompt,
    fixture_anthropic_message_chunk,
    fixture_anthropic_message_chunks,
):
    """Tests `AnthropicPrompt.stream` returns the expected response when called with a wrapper."""
    mock_stream.return_value = fixture_anthropic_message_chunks

    wrapper = MagicMock()
    wrapper.return_value = Anthropic()

    fixture_anthropic_test_prompt.call_params.wrapper = wrapper

    stream = fixture_anthropic_test_prompt.stream()
    for chunk in stream:
        assert isinstance(chunk, AnthropicCompletionChunk)
        assert chunk.chunk == fixture_anthropic_message_chunk
    wrapper.assert_called_once()
    mock_stream.assert_called_once_with(
        model=fixture_anthropic_test_prompt.call_params.model,
        messages=fixture_anthropic_test_prompt.messages,
        temperature=0.3,
        max_tokens=fixture_anthropic_test_prompt.call_params.max_tokens,
        timeout=fixture_anthropic_test_prompt.call_params.timeout,
    )


@patch(
    "anthropic.resources.messages.AsyncMessages.stream",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_anthropic_prompt_async_stream_with_wrapper(
    mock_stream,
    fixture_anthropic_test_prompt,
    fixture_anthropic_message_chunk,
    fixture_anthropic_async_message_chunks,
):
    """Tests `AnthropicPrompt.async_stream` returns the expected response when called with a wrapper."""
    mock_stream.return_value = fixture_anthropic_async_message_chunks

    wrapper = MagicMock()
    wrapper.return_value = AsyncAnthropic()

    fixture_anthropic_test_prompt.call_params.async_wrapper = wrapper

    stream = fixture_anthropic_test_prompt.async_stream()
    async for chunk in stream:
        assert isinstance(chunk, AnthropicCompletionChunk)
        assert chunk.chunk == fixture_anthropic_message_chunk
    wrapper.assert_called_once()
    mock_stream.assert_called_once_with(
        model=fixture_anthropic_test_prompt.call_params.model,
        messages=fixture_anthropic_test_prompt.messages,
        temperature=0.3,
        max_tokens=fixture_anthropic_test_prompt.call_params.max_tokens,
        timeout=fixture_anthropic_test_prompt.call_params.timeout,
    )
