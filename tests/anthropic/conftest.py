"""Fixtures for Mirascope's Anthropic module tests."""
from typing import Type

import pytest
from anthropic.types import (
    ContentBlock,
    ContentBlockDeltaEvent,
    Message,
    MessageStartEvent,
    MessageStreamEvent,
    TextDelta,
    Usage,
)

from mirascope.anthropic.calls import AnthropicCall
from mirascope.anthropic.tools import AnthropicTool
from mirascope.anthropic.types import AnthropicCallParams, AnthropicCallResponseChunk


@pytest.fixture()
def fixture_anthropic_test_call():
    """Returns an Anthropic test prompt."""

    class AnthropicTestCall(AnthropicCall):
        prompt_template = "This is a test prompt for Anthropic."

        call_params = AnthropicCallParams(temperature=0.3)

    return AnthropicTestCall(api_key="test")


@pytest.fixture()
def fixture_anthropic_test_messages_call():
    """Returns an Anthropic test prompt with messages."""

    class AnthropicTestMessagesPrompt(AnthropicCall):
        prompt_template = """
        SYSTEM:
        System message

        USER:
        User message
        """

        call_params = AnthropicCallParams(temperature=0.3)

    return AnthropicTestMessagesPrompt(api_key="test")


@pytest.fixture()
def fixture_anthropic_message() -> Message:
    """Returns an Anthropic message."""
    return Message(
        id="0",
        content=[ContentBlock(text="test", type="text")],
        model="claude-3-haiku-20240307",
        role="assistant",
        type="message",
        usage=Usage(input_tokens=0, output_tokens=0),
    )


@pytest.fixture()
def fixture_anthropic_message_with_tools_bad_stop_reason(
    fixture_anthropic_message_with_tools: Message,
) -> Message:
    """Returns an Anthropic message with tools XML in the response"""
    fixture_anthropic_message_with_tools.stop_reason = "max_tokens"
    return fixture_anthropic_message_with_tools


@pytest.fixture()
def fixture_anthropic_call_response_chunks_with_tools(
    fixture_anthropic_book_tool: Type[AnthropicTool],
) -> list[AnthropicCallResponseChunk]:
    """Returns a list of content block delta events with tools."""
    chunks: list[MessageStreamEvent] = [
        MessageStartEvent(
            message=Message(
                id="id",
                content=[],
                role="assistant",
                type="message",
                model="test",
                usage=Usage(input_tokens=0, output_tokens=0),
            ),
            type="message_start",
        ),
        ContentBlockDeltaEvent(
            delta=TextDelta(
                text='"tool_name": "AnthropicBookTool", "title": "The Name of the Wind"',
                type="text_delta",
            ),
            index=0,
            type="content_block_delta",
        ),
        ContentBlockDeltaEvent(
            delta=TextDelta(text=', "author": "Patrick Rothfuss"}', type="text_delta"),
            index=1,
            type="content_block_delta",
        ),
        ContentBlockDeltaEvent(
            delta=TextDelta(
                text='{"tool_name": "AnthropicBookTool", "title": "The Name of the Wind"',
                type="text_delta",
            ),
            index=2,
            type="content_block_delta",
        ),
        ContentBlockDeltaEvent(
            delta=TextDelta(text=', "author": "Patrick Rothfuss"}', type="text_delta"),
            index=3,
            type="content_block_delta",
        ),
    ]
    return [
        AnthropicCallResponseChunk(
            chunk=chunk,
            tool_types=[fixture_anthropic_book_tool],
            response_format="json",
        )
        for chunk in chunks
    ]


@pytest.fixture()
def fixture_anthropic_call_response_chunk_with_bad_tool(
    fixture_anthropic_book_tool: Type[AnthropicTool],
) -> AnthropicCallResponseChunk:
    """Returns a content block delta event with a bad tool name."""
    return AnthropicCallResponseChunk(
        chunk=ContentBlockDeltaEvent(
            delta=TextDelta(
                text='"tool_name": "BadTool"',
                type="text_delta",
            ),
            index=3,
            type="content_block_delta",
        ),
        tool_types=[fixture_anthropic_book_tool],
        response_format="json",
    )
