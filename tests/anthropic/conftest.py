"""Fixtures for Mirascope's Anthropic module tests."""
from contextlib import asynccontextmanager, contextmanager
from typing import Type

import pytest
from anthropic.types import (
    ContentBlock,
    ContentBlockDeltaEvent,
    Message,
    TextDelta,
    Usage,
)
from anthropic.types.beta.tools import ToolsBetaMessage, ToolUseBlock

from mirascope.anthropic.calls import AnthropicCall
from mirascope.anthropic.tools import AnthropicTool
from mirascope.anthropic.types import AnthropicCallParams


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
        model="test",
        role="assistant",
        type="message",
        usage=Usage(input_tokens=0, output_tokens=0),
    )


@pytest.fixture()
def fixture_anthropic_message_with_tools() -> ToolsBetaMessage:
    """Returns an Anthropic message with tools XML in the response"""
    return ToolsBetaMessage(
        id="0",
        content=[
            ContentBlock(type="text", text="test"),
            ToolUseBlock(
                id="test",
                name="BookTool",
                input={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
                type="tool_use",
            ),
        ],
        model="test",
        role="assistant",
        type="message",
        usage=Usage(input_tokens=0, output_tokens=0),
        stop_reason="tool_use",
    )


@pytest.fixture()
def fixture_anthropic_message_with_tools_bad_stop_reason(
    fixture_anthropic_message_with_tools: Message,
) -> Message:
    """Returns an Anthropic message with tools XML in the response"""
    fixture_anthropic_message_with_tools.stop_reason = "max_tokens"
    return fixture_anthropic_message_with_tools


@pytest.fixture()
def fixture_anthropic_message_chunk():
    """Returns an Anthropic message."""
    return ContentBlockDeltaEvent(
        delta=TextDelta(text="test", type="text_delta"),
        index=1,
        type="content_block_delta",
    )


@pytest.fixture()
def fixture_anthropic_message_chunks(
    fixture_anthropic_message_chunk,
):
    """Returns a context managed stream."""

    @contextmanager
    def chunks():
        yield [fixture_anthropic_message_chunk] * 3

    return chunks()


@pytest.fixture()
def fixture_anthropic_async_message_chunks(fixture_anthropic_message_chunk):
    """Returns a context managed async stream"""

    async def generator():
        yield fixture_anthropic_message_chunk

    @asynccontextmanager
    async def async_chunks():
        yield generator()

    return async_chunks()


class BookTool(AnthropicTool):
    title: str
    author: str


@pytest.fixture()
def fixture_anthropic_book_tool() -> Type[BookTool]:
    """Returns the `BookTool` type definition."""

    return BookTool
