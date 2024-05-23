"""Tests for Anthropic tool streaming classes."""

import pytest

from mirascope.anthropic.tool_streams import AnthropicToolStream
from mirascope.anthropic.types import AnthropicCallResponseChunk


def test_anthropic_tool_stream_from_stream(
    fixture_anthropic_call_response_chunks_with_tools: list[AnthropicCallResponseChunk],
) -> None:
    """Tests streaming tools from chunks."""

    def generator():
        for chunk in fixture_anthropic_call_response_chunks_with_tools:
            yield chunk

    tools = list(AnthropicToolStream.from_stream(generator(), allow_partial=True))
    assert len(tools) == 6
    assert tools[0] is not None and tools[0].args == {
        "title": "The Name of the Wind",
        "author": None,
    }
    assert tools[1] is not None and tools[1].args == {
        "title": "The Name of the Wind",
        "author": "Patrick Rothfuss",
    }
    assert tools[2] is None
    assert tools[3] is not None and tools[3].args == {
        "title": "The Name of the Wind",
        "author": None,
    }
    assert tools[4] is not None and tools[4].args == {
        "title": "The Name of the Wind",
        "author": "Patrick Rothfuss",
    }
    assert tools[5] is None

    tools = list(AnthropicToolStream.from_stream(generator(), allow_partial=False))
    assert len(tools) == 4


def test_anthropic_tool_stream_bad_tool_name(
    fixture_anthropic_call_response_chunk_with_bad_tool: AnthropicCallResponseChunk,
) -> None:
    """Tests that a runtime error is thrown when a tool has a bad name."""

    def generator_partial():
        yield fixture_anthropic_call_response_chunk_with_bad_tool

    with pytest.raises(RuntimeError):
        list(AnthropicToolStream.from_stream(generator_partial(), allow_partial=True))

    def generator():
        fixture_anthropic_call_response_chunk_with_bad_tool.chunk.delta.text += "}"
        yield fixture_anthropic_call_response_chunk_with_bad_tool

    with pytest.raises(RuntimeError):
        list(AnthropicToolStream.from_stream(generator(), allow_partial=False))


def test_anthropic_tool_stream_missing_tool_name(
    fixture_anthropic_call_response_chunk_with_bad_tool: AnthropicCallResponseChunk,
) -> None:
    """Tests that a runtime error is thrown when a tool has a bad name."""

    def generator():
        fixture_anthropic_call_response_chunk_with_bad_tool.chunk.delta.text = "}"
        yield fixture_anthropic_call_response_chunk_with_bad_tool

    with pytest.raises(RuntimeError):
        list(AnthropicToolStream.from_stream(generator()))


def test_anthropic_tool_stream_not_json_mode(
    fixture_anthropic_call_response_chunk_with_bad_tool: AnthropicCallResponseChunk,
) -> None:
    """Tests a runtime error is thrown when not using json mode for a tool stream."""

    def generator():
        fixture_anthropic_call_response_chunk_with_bad_tool.response_format = None
        yield fixture_anthropic_call_response_chunk_with_bad_tool

    with pytest.raises(ValueError):
        list(AnthropicToolStream.from_stream(generator()))


def test_anthropic_tool_stream_no_tool_types(
    fixture_anthropic_call_response_chunks_with_tools: list[AnthropicCallResponseChunk],
) -> None:
    """Tests a runtime error is thrown when not using json mode for a tool stream."""

    def generator():
        for chunk in fixture_anthropic_call_response_chunks_with_tools:
            chunk.tool_types = None
            yield chunk

    tools = list(AnthropicToolStream.from_stream(generator()))
    assert len(tools) == 0


@pytest.mark.asyncio
async def test_anthropic_tool_stream_from_async_stream(
    fixture_anthropic_call_response_chunks_with_tools: list[AnthropicCallResponseChunk],
) -> None:
    """Tests streaming tools from chunks."""

    async def generator():
        for chunk in fixture_anthropic_call_response_chunks_with_tools:
            yield chunk

    tools = [
        tool
        async for tool in AnthropicToolStream.from_async_stream(
            generator(), allow_partial=True
        )
    ]
    assert len(tools) == 6
    assert tools[0] is not None and tools[0].args == {
        "title": "The Name of the Wind",
        "author": None,
    }
    assert tools[1] is not None and tools[1].args == {
        "title": "The Name of the Wind",
        "author": "Patrick Rothfuss",
    }
    assert tools[2] is None
    assert tools[3] is not None and tools[3].args == {
        "title": "The Name of the Wind",
        "author": None,
    }
    assert tools[4] is not None and tools[4].args == {
        "title": "The Name of the Wind",
        "author": "Patrick Rothfuss",
    }
    assert tools[5] is None
