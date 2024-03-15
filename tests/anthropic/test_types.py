"""Tests for Mirascope's Anthropic types module."""
from anthropic.types import (
    ContentBlock,
    ContentBlockDeltaEvent,
    ContentBlockStartEvent,
    ContentBlockStopEvent,
    Message,
)

from mirascope.anthropic.types import AnthropicCallResponse, AnthropicCallResponseChunk


def test_anthropic_completion(fixture_anthropic_message: Message):
    """Tests the `AnthropicCompletion` class."""
    response = AnthropicCallResponse(
        response=fixture_anthropic_message, start_time=0, end_time=1
    )
    assert response.content == "test"
    assert response.tools is None
    assert response.tool is None


def test_anthropic_completion_chunk(
    fixture_anthropic_message_chunk: ContentBlockDeltaEvent,
):
    """Tests the `AnthropicCompletionChunk` class."""
    chunk = AnthropicCallResponseChunk(chunk=fixture_anthropic_message_chunk)
    assert chunk.content == "test"

    chunk = AnthropicCallResponseChunk(
        chunk=ContentBlockStartEvent(
            content_block=ContentBlock(text="test_start", type="text"),
            index=0,
            type="content_block_start",
        )
    )
    assert chunk.content == "test_start"
    assert chunk.type == "content_block_start"

    chunk = AnthropicCallResponseChunk(
        chunk=ContentBlockStopEvent(index=2, type="content_block_stop")
    )
    assert chunk.content == ""
    assert chunk.type == "content_block_stop"
