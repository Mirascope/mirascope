"""Tests the `mistral._utils.handle_stream` module."""

import pytest
from mistralai.models.chat_completion import (
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    DeltaMessage,
    FinishReason,
    FunctionCall,
    ToolCall,
    ToolType,
)

from mirascope.core.mistral._utils._handle_stream import (
    handle_stream,
    handle_stream_async,
)
from mirascope.core.mistral.tool import MistralTool


class FormatBook(MistralTool):
    """Returns the title and author nicely formatted."""

    title: str
    author: str

    def call(self) -> None:
        """Dummy call."""


@pytest.fixture()
def mock_chunks() -> list[ChatCompletionStreamResponse]:
    """Returns a list of mock `ChatCompletionStreamResponse` instances."""

    new_tool_call = ToolCall(
        id="id",
        function=FunctionCall(
            arguments="",
            name="FormatBook",
        ),
        type=ToolType.function,
    )
    tool_call = ToolCall(
        id="null",
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
        type=ToolType.function,
    )
    return [
        ChatCompletionStreamResponse(
            id="id",
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(content="content", tool_calls=None),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        ChatCompletionStreamResponse(
            id="id",
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[new_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        ChatCompletionStreamResponse(
            id="id",
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        ChatCompletionStreamResponse(
            id="id",
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[new_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        ChatCompletionStreamResponse(
            id="id",
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        ChatCompletionStreamResponse(
            id="id",
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(content=None, tool_calls=None),
                    finish_reason=FinishReason.tool_calls,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
    ]


def test_handle_stream(mock_chunks: list[ChatCompletionStreamResponse]) -> None:
    """Tests the `handle_stream` function."""

    result = list(handle_stream((c for c in mock_chunks), tool_types=[FormatBook]))
    # Check we get three tuples back.
    # (chunk, None), (chunk, FormatBook), (chunk, FormatBook)
    assert len(result) == 3
    assert result[0][1] is None
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )


@pytest.mark.asyncio
async def test_handle_stream_async(
    mock_chunks: list[ChatCompletionStreamResponse],
) -> None:
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
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
