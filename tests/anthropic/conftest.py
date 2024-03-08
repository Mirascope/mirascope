"""Fixtures for Mirascope's Anthropic module tests."""
from contextlib import asynccontextmanager, contextmanager

import pytest
from anthropic.types import (
    ContentBlock,
    ContentBlockDeltaEvent,
    Message,
    TextDelta,
    Usage,
)

from mirascope.anthropic.prompt import AnthropicPrompt
from mirascope.anthropic.types import (
    AnthropicCallParams,
)


@pytest.fixture()
def fixture_anthropic_test_prompt():
    """Returns an Anthropic test prompt."""

    class AnthropicTestPrompt(AnthropicPrompt):
        """This is a test prompt for Anthropic."""

        call_params = AnthropicCallParams(temperature=0.3)

    return AnthropicTestPrompt(api_key="test")


@pytest.fixture()
def fixture_anthropic_test_messages_prompt():
    """Returns an Anthropic test prompt with messages."""

    class AnthropicTestMessagesPrompt(AnthropicPrompt):
        """
        USER:
        User message

        ASSISTANT:
        System message

        USER:
        User message
        """

        call_params = AnthropicCallParams(temperature=0.3)

    return AnthropicTestMessagesPrompt(api_key="test")


@pytest.fixture()
def fixture_anthropic_message():
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

    @asynccontextmanager
    async def async_chunks():
        yield [fixture_anthropic_message_chunk] * 3

    return async_chunks()
