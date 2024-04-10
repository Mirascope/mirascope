"""Tests for OpenAI tool streaming classes."""
from typing import Type

import pytest
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.completion_create_params import ResponseFormat

from mirascope.openai.tool_streams import OpenAIToolStream
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import OpenAICallResponseChunk


def test_openai_tool_stream_from_stream(
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_chunks_with_tools: list[ChatCompletionChunk],
) -> None:
    """Tests streaming tools from chunks."""

    def generator():
        for chunk in fixture_chat_completion_chunks_with_tools * 2:
            yield OpenAICallResponseChunk(
                chunk=chunk, tool_types=[fixture_my_openai_tool]
            )

    tools = list(OpenAIToolStream.from_stream(generator(), allow_partial=True))
    assert len(tools) == 7
    assert tools[0] is not None and tools[0].args == {
        "param": "param",
        "optional": None,
    }
    assert tools[1] is not None and tools[1].args == {"param": "param", "optional": 0}
    assert tools[2] is not None and tools[2].args == {"param": "param", "optional": 0}
    assert tools[3] is None
    assert tools[4] is not None and tools[4].args == {
        "param": "param",
        "optional": None,
    }
    assert tools[5] is not None and tools[5].args == {"param": "param", "optional": 0}
    assert tools[6] is not None and tools[6].args == {"param": "param", "optional": 0}


def test_openai_tool_stream_bad_tool_name(
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_chunk_with_tools: ChatCompletionChunk,
) -> None:
    """Tests that a runtime error is thrown when a tool has a bad name."""

    def generator():
        chunk_copy = fixture_chat_completion_chunk_with_tools.model_copy()
        chunk_copy.choices[0].delta.tool_calls[0].function.name = "BadToolName"
        yield OpenAICallResponseChunk(
            chunk=chunk_copy, tool_types=[fixture_my_openai_tool]
        )

    with pytest.raises(RuntimeError):
        list(OpenAIToolStream.from_stream(generator(), allow_partial=True))


@pytest.mark.asyncio
async def test_openai_tool_stream_from_async_stream(
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_chunks_with_tools: list[ChatCompletionChunk],
) -> None:
    """Tests streaming tools from chunks."""

    async def async_generator():
        for chunk in fixture_chat_completion_chunks_with_tools * 2:
            yield OpenAICallResponseChunk(
                chunk=chunk, tool_types=[fixture_my_openai_tool]
            )

    tools = []
    async for tool in OpenAIToolStream.from_async_stream(
        async_generator(), allow_partial=True
    ):
        tools.append(tool)
    assert len(tools) == 7
    assert tools[0] is not None and tools[0].args == {
        "param": "param",
        "optional": None,
    }
    assert tools[1] is not None and tools[1].args == {"param": "param", "optional": 0}
    assert tools[2] is not None and tools[2].args == {"param": "param", "optional": 0}
    assert tools[3] is None
    assert tools[4] is not None and tools[4].args == {
        "param": "param",
        "optional": None,
    }
    assert tools[5] is not None and tools[5].args == {"param": "param", "optional": 0}
    assert tools[6] is not None and tools[6].args == {"param": "param", "optional": 0}


def test_openai_tool_stream_json_mode(
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_chunk_with_tools: ChatCompletionChunk,
) -> None:
    """Tests streaming tools in JSON mode."""

    def generator():
        chunk_copy = fixture_chat_completion_chunk_with_tools.model_copy()
        chunk_copy.response_format = "json_object"
        chunk_copy.choices[0].delta.content = '{"param": "param", "optional": 0}'
        yield OpenAICallResponseChunk(
            chunk=chunk_copy,
            tool_types=[fixture_my_openai_tool],
            response_format=ResponseFormat(type="json_object"),
        )

    tools = list(OpenAIToolStream.from_stream(generator()))
    assert len(tools) == 1
    assert tools[0] is not None and tools[0].args == {"param": "param", "optional": 0}


def test_openai_tool_stream_json_mode_partial(
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_chunk_with_tools: ChatCompletionChunk,
) -> None:
    """Tests streaming partial tools in JSON mode."""

    def generator():
        chunk_copy = fixture_chat_completion_chunk_with_tools.model_copy()
        chunk_copy.response_format = "json_object"
        chunk_copy.choices[0].delta.content = '{"param": "param"'
        yield OpenAICallResponseChunk(
            chunk=chunk_copy.model_copy(),
            tool_types=[fixture_my_openai_tool],
            response_format=ResponseFormat(type="json_object"),
        )
        chunk_copy.choices[0].delta.content = ', "optional": 0}'
        yield OpenAICallResponseChunk(
            chunk=chunk_copy,
            tool_types=[fixture_my_openai_tool],
            response_format=ResponseFormat(type="json_object"),
        )

    tools = list(OpenAIToolStream.from_stream(generator(), allow_partial=True))
    assert len(tools) == 3
    assert tools[0] is not None and tools[0].args == {
        "param": "param",
        "optional": None,
    }
    assert tools[1] is not None and tools[1].args == {"param": "param", "optional": 0}
    assert tools[2] is not None and tools[2].args == {"param": "param", "optional": 0}


def test_openai_tool_stream_no_tool_types(
    fixture_chat_completion_chunk_with_tools: ChatCompletionChunk,
) -> None:
    """Tests that None is returned when chunk.tool_types is not set."""

    def generator():
        yield OpenAICallResponseChunk(
            chunk=fixture_chat_completion_chunk_with_tools,
            tool_types=None,
            response_format=ResponseFormat(type="json_object"),
        )

    tools = list(OpenAIToolStream.from_stream(generator(), allow_partial=True))
    assert len(tools) == 0
