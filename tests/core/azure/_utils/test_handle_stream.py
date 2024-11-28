"""Tests the `azure._utils.handle_stream` module."""

from datetime import datetime

import pytest
from azure.ai.inference.models import (
    CompletionsUsage,
    FunctionCall,
    StreamingChatChoiceUpdate,
    StreamingChatCompletionsUpdate,
    StreamingChatResponseMessageUpdate,
    StreamingChatResponseToolCallUpdate,
)

from mirascope.core.azure._utils._handle_stream import (
    handle_stream,
    handle_stream_async,
)
from mirascope.core.azure.tool import AzureTool


class FormatBook(AzureTool):
    """Returns the title and author nicely formatted."""

    title: str
    author: str

    def call(self) -> None:
        """Dummy call."""


@pytest.fixture()
def mock_chunks() -> list[StreamingChatCompletionsUpdate]:
    """Returns a list of mock `ChatCompletionChunk` instances."""

    new_tool_call = StreamingChatResponseToolCallUpdate(
        id="id",
        function=FunctionCall(
            arguments="",
            name="FormatBook",
        ),
    )
    tool_call = StreamingChatResponseToolCallUpdate(
        id="id",
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
    )
    return [
        StreamingChatCompletionsUpdate(
            id="id",
            choices=[
                StreamingChatChoiceUpdate(
                    delta=StreamingChatResponseMessageUpdate(
                        content="content", tool_calls=None
                    ),
                    index=0,
                    finish_reason="stop",
                )
            ],
            created=datetime.fromtimestamp(0),
            model="gpt-4o",
            usage=CompletionsUsage(
                completion_tokens=0, prompt_tokens=0, total_tokens=0
            ),
        ),
        StreamingChatCompletionsUpdate(
            id="id",
            choices=[
                StreamingChatChoiceUpdate(
                    delta=StreamingChatResponseMessageUpdate(
                        content=None,
                        tool_calls=[new_tool_call],
                    ),
                    index=0,
                    finish_reason="stop",
                )
            ],
            created=datetime.fromtimestamp(0),
            model="gpt-4o",
            usage=CompletionsUsage(
                completion_tokens=0, prompt_tokens=0, total_tokens=0
            ),
        ),
        StreamingChatCompletionsUpdate(
            id="id",
            choices=[
                StreamingChatChoiceUpdate(
                    delta=StreamingChatResponseMessageUpdate(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    index=0,
                    finish_reason="stop",
                )
            ],
            created=datetime.fromtimestamp(0),
            model="gpt-4o",
            usage=CompletionsUsage(
                completion_tokens=0, prompt_tokens=0, total_tokens=0
            ),
        ),
        StreamingChatCompletionsUpdate(
            id="id",
            choices=[
                StreamingChatChoiceUpdate(
                    delta=StreamingChatResponseMessageUpdate(
                        content=None,
                        tool_calls=[new_tool_call],
                    ),
                    index=0,
                    finish_reason="stop",
                )
            ],
            created=datetime.fromtimestamp(0),
            model="gpt-4o",
            usage=CompletionsUsage(
                completion_tokens=0, prompt_tokens=0, total_tokens=0
            ),
        ),
        StreamingChatCompletionsUpdate(
            id="id",
            choices=[
                StreamingChatChoiceUpdate(
                    delta=StreamingChatResponseMessageUpdate(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    index=0,
                    finish_reason="stop",
                )
            ],
            created=datetime.fromtimestamp(0),
            model="gpt-4o",
            usage=CompletionsUsage(
                completion_tokens=0, prompt_tokens=0, total_tokens=0
            ),
        ),
        StreamingChatCompletionsUpdate(
            id="id",
            choices=[
                StreamingChatChoiceUpdate(
                    delta=StreamingChatResponseMessageUpdate(
                        content=None, tool_calls=None
                    ),
                    finish_reason="tool_calls",
                    index=0,
                )
            ],
            created=datetime.fromtimestamp(0),
            model="gpt-4o",
            usage=CompletionsUsage(
                completion_tokens=0, prompt_tokens=0, total_tokens=0
            ),
        ),
    ]


def test_handle_stream(mock_chunks: list[StreamingChatCompletionsUpdate]) -> None:
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
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )


@pytest.mark.asyncio
async def test_handle_stream_async(
    mock_chunks: list[StreamingChatCompletionsUpdate],
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
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
