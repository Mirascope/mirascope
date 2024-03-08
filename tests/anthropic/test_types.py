"""Tests for Mirascope's Anthropic types module."""
from anthropic.types import ContentBlock, ContentBlockStartEvent, ContentBlockStopEvent

from mirascope.anthropic.types import AnthropicCompletion, AnthropicCompletionChunk


def test_anthropic_completion(fixture_anthropic_message):
    """Tests the `AnthropicCompletion` class."""
    completion = AnthropicCompletion(
        completion=fixture_anthropic_message, start_time=0, end_time=1
    )
    assert str(completion) == "test"


def test_anthropic_completion_chunk(fixture_anthropic_message_chunk):
    """Tests the `AnthropicCompletionChunk` class."""
    chunk = AnthropicCompletionChunk(chunk=fixture_anthropic_message_chunk)
    assert str(chunk) == "test"

    chunk = AnthropicCompletionChunk(
        chunk=ContentBlockStartEvent(
            content_block=ContentBlock(text="test_start", type="text"),
            index=0,
            type="content_block_start",
        )
    )
    assert str(chunk) == "test_start"
    assert chunk.type == "content_block_start"

    chunk = AnthropicCompletionChunk(
        chunk=ContentBlockStopEvent(index=2, type="content_block_stop")
    )
    assert str(chunk) == ""
    assert chunk.type == "content_block_stop"
