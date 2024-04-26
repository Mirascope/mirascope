"""Fixtures for groq module tests."""
from typing import Type

import pytest
from groq.lib.chat_completion_chunk import (
    ChatCompletionChunk,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
from groq.lib.chat_completion_chunk import Choice as ChunkChoice
from groq.lib.chat_completion_chunk import (
    ChoiceLogprobs as ChunkChoiceLogprobs,
)
from groq.types.chat.chat_completion import (
    ChatCompletion,
    Choice,
    ChoiceLogprobs,
    ChoiceMessage,
    ChoiceMessageToolCall,
    ChoiceMessageToolCallFunction,
    Usage,
)

from mirascope.groq.tools import GroqTool


@pytest.fixture()
def fixture_chat_message() -> ChoiceMessage:
    """Returns a `ChatMessage` instance."""
    return ChoiceMessage(role="assistant", content="test content", tool_calls=[])


@pytest.fixture()
def fixture_chat_completion_response(
    fixture_chat_message: ChoiceMessage,
) -> ChatCompletion:
    """Returns a `ChatCompletion` instance."""
    return ChatCompletion(
        id="test",
        object="chat.completion",
        created=0,
        model="llama2-70b-4096",
        choices=[
            Choice(
                index=0,
                message=fixture_chat_message,
                finish_reason="stop",
                logprobs=ChoiceLogprobs(),
            )
        ],
        usage=Usage(prompt_tokens=1, completion_tokens=1),
    )


class BookTool(GroqTool):
    title: str
    author: str


@pytest.fixture()
def fixture_book_tool() -> Type[BookTool]:
    """Returns the `BookTool` type definition."""

    return BookTool


@pytest.fixture()
def fixture_book_tool_instance() -> BookTool:
    """Returns a `BookTool` instance."""
    return BookTool(
        tool_call=ChoiceMessageToolCall(
            id="id",
            function=ChoiceMessageToolCallFunction(
                name="BookTool",
                arguments='{\n  "title": "The Name of the Wind",\n  "author": "Patrick Rothfuss"}',
            ),
            type="function",
        ),
        title="The Name of the Wind",
        author="Patrick Rothfuss",
    )


@pytest.fixture()
def fixture_expected_book_tool_instance() -> BookTool:
    """Returns the expected `BookTool` instance for testing."""
    return BookTool(
        title="The Name of the Wind",
        author="Patrick Rothfuss",
        tool_call=ChoiceMessageToolCall(
            id="null",
            function=ChoiceMessageToolCallFunction(
                name="BookTool",
                arguments='{"title": "The Name of the Wind","author": "Patrick Rothfuss"}',
            ),
        ),
    )


@pytest.fixture()
def fixture_chat_completion_response_with_tools() -> ChatCompletion:
    """Returns a `ChatCompletion` with tools."""
    return ChatCompletion(
        id="test tool",
        object="chat.completion",
        created=1,
        model="tests",
        choices=[
            Choice(
                index=0,
                message=ChoiceMessage(
                    role="assistant",
                    content="",
                    tool_calls=[
                        ChoiceMessageToolCall(
                            id="null",
                            function=ChoiceMessageToolCallFunction(
                                name="BookTool",
                                arguments='{"title": "The Name of the Wind","author": "Patrick Rothfuss"}',
                            ),
                        )
                    ],
                ),
                finish_reason="tool_calls",
                logprobs=ChoiceLogprobs(),
            )
        ],
        usage=Usage(prompt_tokens=1, completion_tokens=1),
    )


@pytest.fixture()
def fixture_chat_completion_response_with_tools_bad_stop_sequence(
    fixture_chat_completion_response_with_tools: ChatCompletion,
) -> ChatCompletion:
    """Returns a `ChatCompletion` with tools."""
    fixture_chat_completion_response_with_tools.choices[0].finish_reason = "stop"  # type: ignore
    return fixture_chat_completion_response_with_tools


@pytest.fixture()
def fixture_chat_completion_stream_response() -> list[ChatCompletionChunk]:
    """Returns a list of `ChatCompletionChunk` chunks."""
    return [
        ChatCompletionChunk(
            id="test",
            model="llama2-70b-4096",
            choices=[
                ChunkChoice(
                    index=0,
                    delta=ChoiceDelta(role="assistant", content="A"),
                    finish_reason="stop",
                    logprobs=ChunkChoiceLogprobs(),
                )
            ],
            created=0,
            object="",
            system_fingerprint="",
            x_groq=None,
        ),
        ChatCompletionChunk(
            id="test",
            model="llama2-70b-4096",
            choices=[
                ChunkChoice(
                    index=0,
                    delta=ChoiceDelta(role="assistant", content="B"),
                    finish_reason="stop",
                    logprobs=ChunkChoiceLogprobs(),
                )
            ],
            created=0,
            object="",
            system_fingerprint="",
            x_groq=None,
        ),
    ]


@pytest.fixture()
def fixture_chat_completion_stream_response_with_tools() -> list[ChatCompletionChunk]:
    """Returns a list of `ChatCompletionStreamResponse` chunks with tool calls."""
    tool_call = ChoiceDeltaToolCall(
        index=0,
        id="null",
        function=ChoiceDeltaToolCallFunction(
            name="BookTool",
            arguments='{"title": "The Name of the Wind","author": "Patrick Rothfuss"}',
        ),
    )
    return [
        ChatCompletionChunk(
            id="test",
            model="llama2-70b-4096",
            choices=[
                ChunkChoice(
                    index=0,
                    delta=ChoiceDelta(
                        content="",
                        role="assistant",
                        tool_calls=[tool_call],
                    ),
                    finish_reason="stop",
                    logprobs=ChunkChoiceLogprobs(),
                )
            ],
            created=0,
            object="",
            system_fingerprint="",
            x_groq=None,
        ),
        ChatCompletionChunk(
            id="test",
            model="llama2-70b-4096",
            choices=[
                ChunkChoice(
                    index=0,
                    delta=ChoiceDelta(
                        content="",
                        role="assistant",
                        tool_calls=[tool_call],
                    ),
                    finish_reason="stop",
                    logprobs=ChunkChoiceLogprobs(),
                )
            ],
            created=0,
            object="",
            system_fingerprint="",
            x_groq=None,
        ),
    ]


@pytest.fixture()
def fixture_chat_completion_with_tools_json_mode(
    fixture_chat_completion_response: ChatCompletion,
) -> ChatCompletion:
    """Returns a chat completion with a JSON mode tool call."""
    fixture_chat_completion_response.choices[
        0
    ].message.content = (
        '{\n  "title": "The Name of the Wind",\n  "author": "Patrick Rothfuss"}'
    )
    return fixture_chat_completion_response
