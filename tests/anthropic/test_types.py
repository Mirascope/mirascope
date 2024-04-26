"""Tests for Mirascope's Anthropic types module."""
from typing import Type

import pytest
from anthropic.types import (
    ContentBlock,
    ContentBlockDeltaEvent,
    ContentBlockStartEvent,
    ContentBlockStopEvent,
    Message,
)

from mirascope.anthropic.tools import AnthropicTool
from mirascope.anthropic.types import AnthropicCallResponse, AnthropicCallResponseChunk


def test_anthropic_call_response(fixture_anthropic_message: Message):
    """Tests the `AnthropicCallResponse` class."""
    response = AnthropicCallResponse(
        response=fixture_anthropic_message, start_time=0, end_time=1
    )
    assert response.content == "test"
    assert response.tools is None
    assert response.tool is None
    assert response.dump() == {
        "start_time": 0,
        "end_time": 1,
        "output": fixture_anthropic_message.model_dump(),
    }


def test_anthropic_call_response_with_tools_bad_stop_reason(
    fixture_anthropic_message_with_tools_bad_stop_reason: Message,
    fixture_anthropic_book_tool: Type[AnthropicTool],
):
    """Tests the `AnthropicCallResponse` class with a tool and bad stop reason."""
    response = AnthropicCallResponse(
        response=fixture_anthropic_message_with_tools_bad_stop_reason,
        tool_types=[fixture_anthropic_book_tool],
        start_time=0,
        end_time=1,
    )
    with pytest.raises(RuntimeError):
        response.tool


def test_anthropic_call_response_chunk(
    fixture_anthropic_message_chunk: ContentBlockDeltaEvent,
):
    """Tests the `AnthropicCallResponseChunk` class."""
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
