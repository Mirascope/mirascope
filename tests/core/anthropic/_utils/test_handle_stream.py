"""Tests the `anthropic._utils.handle_stream` module."""

from unittest.mock import MagicMock

import pytest
from anthropic.types import (
    Message,
    MessageDeltaUsage,
    MessageStreamEvent,
    RawContentBlockDeltaEvent,
    RawContentBlockStartEvent,
    RawContentBlockStopEvent,
    RawMessageDeltaEvent,
    RawMessageStartEvent,
    RawMessageStopEvent,
    TextBlock,
    TextDelta,
    ToolUseBlock,
    Usage,
)

try:
    from anthropic.types import (
        InputJsonDelta as InputJSONDelta,  # pyright: ignore [reportAttributeAccessIssue]
    )
except ImportError:
    from anthropic.types import (
        InputJSONDelta,  # pyright: ignore [reportAttributeAccessIssue]
    )

from anthropic.types.raw_message_delta_event import Delta

from mirascope.core.anthropic._utils._handle_stream import (
    _handle_chunk,
    handle_stream,
    handle_stream_async,
)
from mirascope.core.anthropic.tool import AnthropicTool


class FormatBook(AnthropicTool):
    """Returns the title and author nicely formatted."""

    title: str
    author: str

    def call(self) -> None:
        """Dummy call."""


@pytest.fixture()
def mock_chunks() -> list[MessageStreamEvent]:
    """Returns a list of mock `MessageStreamEvent` instances."""
    return [
        RawMessageStartEvent(
            message=Message(
                id="msg_01UqKdZkJHmGJJRpNLMsBeAL",
                content=[],
                model="claude-3-5-sonnet-20240620",
                role="assistant",
                stop_reason=None,
                stop_sequence=None,
                type="message",
                usage=Usage(input_tokens=574, output_tokens=3),
            ),
            type="message_start",
        ),
        RawContentBlockStartEvent(
            content_block=TextBlock(text="", type="text"),
            index=0,
            type="content_block_start",
        ),
        RawContentBlockDeltaEvent(
            delta=TextDelta(text="Certainly! I can help", type="text_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockStopEvent(index=0, type="content_block_stop"),
        RawContentBlockStartEvent(
            content_block=ToolUseBlock(
                id="id",
                input={},
                name="FormatBook",
                type="tool_use",
            ),
            index=1,
            type="content_block_start",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJSONDelta(
                partial_json='{"title": "The Name',
                type="input_json_delta",
            ),
            index=1,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJSONDelta(
                partial_json=' of the Wind", "author": ',
                type="input_json_delta",
            ),
            index=1,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJSONDelta(
                partial_json='"Patrick Rothfuss"}',
                type="input_json_delta",
            ),
            index=1,
            type="content_block_delta",
        ),
        RawContentBlockStopEvent(index=1, type="content_block_stop"),
        RawMessageDeltaEvent(
            delta=Delta(stop_reason="tool_use", stop_sequence=None),
            type="message_delta",
            usage=MessageDeltaUsage(output_tokens=127),
        ),
        RawMessageStopEvent(type="message_stop"),
    ]


def test_handle_stream(mock_chunks: list[MessageStreamEvent]) -> None:
    """Tests the `handle_stream` function."""

    result = list(handle_stream((c for c in mock_chunks), tool_types=[FormatBook]))
    assert len(result) == 11
    assert result[0][1] is None
    assert (
        (tool := result[8][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )


@pytest.mark.asyncio
async def test_handle_stream_async(mock_chunks: list[MessageStreamEvent]) -> None:
    """Tests the `handle_stream_async` function."""

    async def generator():
        for chunk in mock_chunks:
            yield chunk

    result = []
    async for t in handle_stream_async(generator(), tool_types=[FormatBook]):
        result.append(t)
    assert len(result) == 11
    assert result[0][1] is None
    assert (
        (tool := result[8][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )


def test_handle_stream_with_partial_tools(
    mock_chunks: list[MessageStreamEvent],
) -> None:
    """Tests the `handle_stream` function with partial tools enabled."""
    result = list(
        handle_stream(
            (c for c in mock_chunks), tool_types=[FormatBook], partial_tools=True
        )
    )

    assert len(result) == 11
    assert result[0][1] is None

    # First partial response
    assert (
        (tool := result[5][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '{"title": "The Name'
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": None, "title": "The Name"}
    )

    # Second partial response
    assert (
        (tool := result[6][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' of the Wind", "author": '
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": None, "title": "The Name of the Wind"}
    )

    # Third partial response
    assert (
        (tool := result[7][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '"Patrick Rothfuss"}'
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": "Patrick Rothfuss", "title": "The Name of the Wind"}
    )

    # Final complete tool
    assert (
        (tool := result[8][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )


@pytest.mark.asyncio
async def test_handle_stream_async_with_partial_tools(
    mock_chunks: list[MessageStreamEvent],
) -> None:
    """Tests the `handle_stream_async` function with partial tools enabled."""

    async def generator():
        for chunk in mock_chunks:
            yield chunk

    result = []
    async for t in handle_stream_async(
        generator(), tool_types=[FormatBook], partial_tools=True
    ):
        result.append(t)

    assert len(result) == 11
    assert result[0][1] is None

    # First partial response
    assert (
        (tool := result[5][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '{"title": "The Name'
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": None, "title": "The Name"}
    )

    # Second partial response
    assert (
        (tool := result[6][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' of the Wind", "author": '
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": None, "title": "The Name of the Wind"}
    )

    # Third partial response
    assert (
        (tool := result[7][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '"Patrick Rothfuss"}'
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": "Patrick Rothfuss", "title": "The Name of the Wind"}
    )

    # Final complete tool
    assert (
        (tool := result[8][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )


def test_handle_chunk_no_tool_types() -> None:
    """Tests the `_handle_chunk` function with no tool types."""
    mock_chunk = MagicMock(spec=MessageStreamEvent)
    mock_current_tool_call = MagicMock(spec=ToolUseBlock)
    buffer, chunk, current_tool_call, current_tool_type = _handle_chunk(
        "",
        mock_chunk,
        mock_current_tool_call,
        None,
        None,
    )
    assert buffer == ""
    assert chunk is None
    assert current_tool_call == mock_current_tool_call
    assert current_tool_type is None
