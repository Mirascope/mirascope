"""Tests for `AnthropicCall`."""
from textwrap import dedent
from typing import AsyncContextManager, ContextManager, Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import ContentBlockDeltaEvent, Message
from pytest import FixtureRequest

from mirascope.anthropic.calls import AnthropicCall
from mirascope.anthropic.tools import AnthropicTool
from mirascope.anthropic.types import (
    AnthropicCallParams,
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
    "anthropic.resources.beta.tools.messages.Messages.create",
    new_callable=MagicMock,
)
def test_anthropic_call_call_json_tools_setup(
    mock_create: MagicMock,
    fixture_anthropic_book_tool: Type[AnthropicTool],
    fixture_anthropic_message_with_tools: Message,
):
    """Tests `AnthropicCall.call` json mode."""
    mock_create.return_value = fixture_anthropic_message_with_tools

    class MyCall(AnthropicCall):
        prompt_template = "SYSTEM: system"
        api_key = "test"
        call_params = AnthropicCallParams(
            system="system",
            tools=[fixture_anthropic_book_tool],
            response_format="json",
            model="test",
        )

    MyCall().call()
    tool_schema = {
        "input_schema": {
            "properties": {
                "title": {"title": "Title", "type": "string"},
                "author": {"title": "Author", "type": "string"},
            },
            "required": ["title", "author"],
            "type": "object",
        },
        "name": "AnthropicBookTool",
        "description": "Correctly formatted and typed parameters extracted from the completion. Must include required parameters and may exclude optional parameters unless present in the text.",
    }
    mock_create.assert_called_once_with(
        model="test",
        stream=False,
        max_tokens=1000,
        timeout=600,
        system="system\nsystem\n\nResponse format: JSON.",
        messages=[
            {
                "role": "assistant",
                "content": dedent(
                    """
        For each JSON you output, output ONLY the fields defined by these schemas. Include a `tool_name` field that EXACTLY MATCHES the tool name found in the schema matching this tool:
        {tool_schema}
        Here is the JSON requested with only the fields defined in the schema you provided:{assistance}
                    """
                )
                .format(tool_schema=str(tool_schema), assistance="\n{")
                .strip(),
            }
        ],
    )


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
