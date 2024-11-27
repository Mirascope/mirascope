"""Tests the `openai._utils.handle_stream` module."""

import pytest
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import (
    Choice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)

from mirascope.core.openai._utils._handle_stream import (
    handle_stream,
    handle_stream_async,
)
from mirascope.core.openai.tool import OpenAITool


class FormatBook(OpenAITool):
    """Returns the title and author nicely formatted."""

    title: str
    author: str

    def call(self) -> None:
        """Dummy call."""


@pytest.fixture()
def mock_chunks() -> list[ChatCompletionChunk]:
    """Returns a list of mock `ChatCompletionChunk` instances."""

    # Initial tool call setup with ID and name
    init_tool_call = ChoiceDeltaToolCall(
        index=0,
        id="id",
        function=ChoiceDeltaToolCallFunction(
            arguments=None,
            name="FormatBook",
        ),
        type="function",
    )

    # First part of the JSON argument
    part1_tool_call = ChoiceDeltaToolCall(
        index=0,
        id=None,
        function=ChoiceDeltaToolCallFunction(
            arguments='{"title": "The Name',
            name=None,
        ),
        type="function",
    )

    # Second part of the JSON argument
    part2_tool_call = ChoiceDeltaToolCall(
        index=0,
        id=None,
        function=ChoiceDeltaToolCallFunction(
            arguments=' of the Wind", "author": ',
            name=None,
        ),
        type="function",
    )

    # Final part of the JSON argument
    part3_tool_call = ChoiceDeltaToolCall(
        index=0,
        id=None,
        function=ChoiceDeltaToolCallFunction(
            arguments='"Patrick Rothfuss"}',
            name=None,
        ),
        type="function",
    )
    tool_call = ChoiceDeltaToolCall(
        index=0,
        id=None,
        function=ChoiceDeltaToolCallFunction(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name=None,
        ),
        type="function",
    )
    return [
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(delta=ChoiceDelta(content="content", tool_calls=None), index=0)
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[init_tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[part1_tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[part2_tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[part3_tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[init_tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(content=None, tool_calls=None),
                    finish_reason="tool_calls",
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
    ]


def test_handle_stream(mock_chunks: list[ChatCompletionChunk]) -> None:
    """Tests the `handle_stream` function."""

    result = list(handle_stream((c for c in mock_chunks), tool_types=[FormatBook]))
    # Check we get three tuples back.
    # (chunk, None), (chunk, FormatBook), (chunk, FormatBook)
    assert len(result) == 3
    assert result[0][1] is None
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )


@pytest.mark.asyncio
async def test_handle_stream_async(mock_chunks: list[ChatCompletionChunk]) -> None:
    """Tests the `handle_stream_async` function."""

    async def generator():
        for chunk in mock_chunks:
            yield chunk

    result = []
    async for t in handle_stream_async(generator(), tool_types=[FormatBook]):
        result.append(t)
    # Check we get three tuples back.
    # (chunk, None), (chunk, FormatBook), (chunk, FormatBook)
    assert len(result) == 3
    assert result[0][1] is None
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )


def test_handle_stream_with_partial_tools(
    mock_chunks: list[ChatCompletionChunk],
) -> None:
    """Tests the `handle_stream` function with partial tools enabled."""
    result = list(
        handle_stream(
            (c for c in mock_chunks), tool_types=[FormatBook], partial_tools=True
        )
    )

    assert len(result) == 7
    assert result[0][1] is None

    # First partial response
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '{"title": "The Name'
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": None, "title": "The Name"}
    )

    # Second partial response
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' of the Wind", "author": '
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": None, "title": "The Name of the Wind"}
    )

    # Third partial response
    assert (
        (tool := result[3][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '"Patrick Rothfuss"}'
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": "Patrick Rothfuss", "title": "The Name of the Wind"}
    )

    # Final complete tool
    assert (
        (tool := result[4][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )


@pytest.mark.asyncio
async def test_handle_stream_async_with_partial_tools(
    mock_chunks: list[ChatCompletionChunk],
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

    assert len(result) == 7
    assert result[0][1] is None

    # First partial response
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '{"title": "The Name'
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": None, "title": "The Name"}
    )

    # Second partial response
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' of the Wind", "author": '
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": None, "title": "The Name of the Wind"}
    )

    # Third partial response
    assert (
        (tool := result[3][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '"Patrick Rothfuss"}'
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"author": "Patrick Rothfuss", "title": "The Name of the Wind"}
    )

    # Final complete tool
    assert (
        (tool := result[4][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )
