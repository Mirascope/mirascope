"""Fixtures for mistral module tests."""

from typing import Type

import pytest
from mistralai.models.chat_completion import (
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    ChatMessage,
    DeltaMessage,
    FinishReason,
    FunctionCall,
    ToolCall,
    ToolType,
)
from mistralai.models.common import UsageInfo

from mirascope.mistral import MistralTool


@pytest.fixture()
def fixture_chat_message():
    """Returns a `ChatMessage` instance."""
    return ChatMessage(
        role="assistant", content="test content", name=None, tool_calls=None
    )


@pytest.fixture()
def fixture_chat_completion_response(
    fixture_chat_message: ChatMessage,
) -> ChatCompletionResponse:
    """Returns a `ChatCompletionResponse` instance."""
    return ChatCompletionResponse(
        id="test",
        object="chat.completion",
        created=0,
        model="open-mixtral-8x7b",
        choices=[
            ChatCompletionResponseChoice(
                index=0, message=fixture_chat_message, finish_reason=None
            )
        ],
        usage=UsageInfo(prompt_tokens=1, total_tokens=2, completion_tokens=1),
    )


class BookTool(MistralTool):
    title: str
    author: str


@pytest.fixture()
def fixture_book_tool() -> Type[BookTool]:
    """Returns the `BookTool` type definition."""

    return BookTool


@pytest.fixture()
def fixture_expected_book_tool_instance() -> BookTool:
    """Returns the expected `BookTool` instance for testing."""
    return BookTool(
        title="The Name of the Wind",
        author="Patrick Rothfuss",
        tool_call=ToolCall(
            id="null",
            type=ToolType.function,
            function=FunctionCall(
                name="BookTool",
                arguments='{"title": "The Name of the Wind","author": "Patrick Rothfuss"}',
            ),
        ),
    )


@pytest.fixture()
def fixture_chat_completion_response_with_tools() -> ChatCompletionResponse:
    """Returns a `ChatCompletionResponse` with tools."""
    return ChatCompletionResponse(
        id="test tool",
        object="chat.completion",
        created=1,
        model="mistral-large-latest",
        choices=[
            ChatCompletionResponseChoice(
                index=0,
                message=ChatMessage(
                    role="assistant",
                    content="",
                    name=None,
                    tool_calls=[
                        ToolCall(
                            id="null",
                            type=ToolType.function,
                            function=FunctionCall(
                                name="BookTool",
                                arguments='{"title": "The Name of the Wind","author": "Patrick Rothfuss"}',
                            ),
                        )
                    ],
                ),
                finish_reason=FinishReason.tool_calls,
            )
        ],
        usage=UsageInfo(prompt_tokens=85, total_tokens=108, completion_tokens=23),
    )


@pytest.fixture()
def fixture_chat_completion_response_with_tools_bad_stop_sequence(
    fixture_chat_completion_response_with_tools: ChatCompletionResponse,
) -> ChatCompletionResponse:
    """Returns a `ChatCompletionResponse` with tools."""
    fixture_chat_completion_response_with_tools.choices[0].finish_reason = "length"  # type: ignore
    return fixture_chat_completion_response_with_tools


@pytest.fixture()
def fixture_chat_completion_stream_response() -> list[ChatCompletionStreamResponse]:
    """Returns a list of `ChatCompletionStreamResponse` chunks."""
    return [
        ChatCompletionStreamResponse(
            id="test",
            model="open-mixtral-8x7b",
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(role="assistant", content="A"),
                    finish_reason=None,
                )
            ],
            usage=UsageInfo(prompt_tokens=1, total_tokens=2, completion_tokens=1),
        ),
        ChatCompletionStreamResponse(
            id="test",
            model="open-mixtral-8x7b",
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(role="assistant", content="B"),
                    finish_reason=None,
                )
            ],
            usage=UsageInfo(prompt_tokens=1, total_tokens=2, completion_tokens=1),
        ),
    ]


@pytest.fixture()
def fixture_chat_completion_stream_response_with_tools() -> (
    list[ChatCompletionStreamResponse]
):
    """Returns a list of `ChatCompletionStreamResponse` chunks with tool calls."""
    tool_call = ToolCall(
        id="null",
        type=ToolType.function,
        function=FunctionCall(
            name="BookTool",
            arguments='{"title": "The Name of the Wind","author": "Patrick Rothfuss"}',
        ),
    )
    return [
        ChatCompletionStreamResponse(
            id="test",
            model="open-mixtral-8x7b",
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        role="assistant",
                        tool_calls=[tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            usage=UsageInfo(prompt_tokens=1, total_tokens=2, completion_tokens=1),
        ),
        ChatCompletionStreamResponse(
            id="test",
            model="open-mixtral-8x7b",
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        role="assistant",
                        tool_calls=[tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            usage=UsageInfo(prompt_tokens=1, total_tokens=2, completion_tokens=1),
        ),
    ]
