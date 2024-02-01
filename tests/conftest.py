"""Fixtures for repeated use in testing."""
from typing import Type

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from pydantic import Field

from mirascope.chat.tools import OpenAITool

from .test_prompts import FooBarPrompt, MessagesPrompt


@pytest.fixture()
def fixture_foobar_prompt() -> FooBarPrompt:
    """Returns a `FooBarPrompt` instance."""
    return FooBarPrompt(foo="foo", bar="bar")


@pytest.fixture()
def fixture_expected_foobar_prompt_str() -> str:
    """Returns the expected string representation of `FooBarPrompt`."""
    return (
        "This is a test prompt about foobar. "
        "This should be on the same line in the template."
        "\n    This should be indented on a new line in the template."
    )


@pytest.fixture()
def fixture_expected_foobar_prompt_messages(
    fixture_expected_foobar_prompt_str,
) -> list[tuple[str, str]]:
    """Returns the expected messages parsed from `FooBarPrompt`."""
    return [("user", fixture_expected_foobar_prompt_str)]


@pytest.fixture()
def fixture_messages_prompt() -> MessagesPrompt:
    """Returns a `MessagesPrompt` instance."""
    return MessagesPrompt(foo="foo", bar="bar")


@pytest.fixture()
def fixture_expected_messages_prompt_messages() -> list[tuple[str, str]]:
    """Returns the expected messages parsed from `MessagesPrompt`."""
    return [
        (
            "system",
            "This is the system message about foo.\n    "
            "This is also the system message.",
        ),
        ("user", "This is the user message about bar."),
        ("tool", "This is the output of calling a tool."),
        (
            "assistant",
            "This is an assistant message about foobar. "
            "This is also part of the assistant message.",
        ),
    ]


@pytest.fixture()
def fixture_string_prompt() -> str:
    """Returns a string prompt."""
    return "This is a test prompt."


@pytest.fixture()
def fixture_expected_string_prompt_messages(
    fixture_string_prompt,
) -> list[tuple[str, str]]:
    """Returns the expected messages parsed from `fixture_string_prompt`."""
    return [("user", fixture_string_prompt)]


@pytest.fixture()
def fixture_chat_completion() -> ChatCompletion:
    """Returns a chat completion."""
    return ChatCompletion(
        id="test_id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="test content 0", role="assistant"
                ),
                **{"logprobs": None},
            ),
            Choice(
                finish_reason="stop",
                index=1,
                message=ChatCompletionMessage(
                    content="test content 1", role="assistant"
                ),
                **{"logprobs": None},
            ),
        ],
        created=0,
        model="test_model",
        object="chat.completion",
    )


@pytest.fixture()
def fixture_chat_completion_with_tools() -> ChatCompletion:
    """Returns a chat completion with tool calls."""
    return ChatCompletion(
        id="test_id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    role="assistant",
                    tool_calls=[
                        ChatCompletionMessageToolCall(
                            id="id",
                            function=Function(
                                arguments='{\n  "param": "param",\n  "optional": 0}',
                                name="MyTool",
                            ),
                            type="function",
                        )
                    ],
                ),
                **{"logprobs": None},
            ),
        ],
        created=0,
        model="test_model",
        object="chat.completion",
    )


@pytest.fixture()
def fixture_chat_completion_with_bad_tools() -> ChatCompletion:
    """Returns a chat completion with tool calls that don't match the tool's schema."""
    return ChatCompletion(
        id="test_id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    role="assistant",
                    tool_calls=[
                        ChatCompletionMessageToolCall(
                            id="id",
                            function=Function(
                                arguments=('{\n  "param": 0,\n  "optional": 0}'),
                                name="MyTool",
                            ),
                            type="function",
                        )
                    ],
                ),
                **{"logprobs": None},
            ),
        ],
        created=0,
        model="test_model",
        object="chat.completion",
    )


@pytest.fixture()
def fixture_chat_completion_chunk() -> ChatCompletionChunk:
    """Returns a chat completion chunk."""
    return ChatCompletionChunk(
        id="test_id",
        choices=[
            ChunkChoice(
                **{"logprobs": None},
                delta=ChoiceDelta(content="I'm"),
                finish_reason="stop",
                index=0,
            ),
            ChunkChoice(
                **{"logprobs": None},
                delta=ChoiceDelta(content="testing"),
                finish_reason="stop",
                index=0,
            ),
        ],
        created=0,
        model="test_model",
        object="chat.completion.chunk",
    )


@pytest.fixture()
def fixture_chat_completion_chunk_with_tools() -> ChatCompletionChunk:
    """Returns a chat completion chunk with tool calls."""
    return ChatCompletionChunk(
        id="test_id",
        choices=[
            ChunkChoice(
                **{"logprobs": None},
                delta=ChoiceDelta(
                    tool_calls=[
                        ChoiceDeltaToolCall(
                            index=0,
                            id="id0",
                            function=ChoiceDeltaToolCallFunction(
                                arguments='{\n "param": "param"'
                            ),
                            type="function",
                        )
                    ]
                ),
                finish_reason="stop",
                index=0,
            ),
            ChunkChoice(
                **{"logprobs": None},
                delta=ChoiceDelta(
                    tool_calls=[
                        ChoiceDeltaToolCall(
                            index=1,
                            id="id1",
                            function=ChoiceDeltaToolCallFunction(
                                arguments=',\n "other": 0\n}'
                            ),
                            type="function",
                        )
                    ]
                ),
                finish_reason="stop",
                index=0,
            ),
        ],
        created=0,
        model="test_model",
        object="chat.completion.chunk",
    )


class MyTool(OpenAITool):
    """A test tool."""

    param: str = Field(..., description="A test parameter.")
    optional: int = 0


@pytest.fixture()
def fixture_my_tool() -> Type[MyTool]:
    """Returns a `MyTool` class."""
    return MyTool


@pytest.fixture()
def fixture_my_tool_instance(fixture_my_tool) -> MyTool:
    """Returns an instance of `MyTool`."""
    return fixture_my_tool(
        param="param",
        optional=0,
        tool_call=ChatCompletionMessageToolCall(
            id="id",
            function=Function(
                arguments='{\n  "param": "param",\n  "optional": 0}',
                name="MyTool",
            ),
            type="function",
        ),
    )


@pytest.fixture()
def fixture_empty_tool() -> Type[OpenAITool]:
    """Returns an `EmptyTool` class."""

    class EmptyTool(OpenAITool):
        """A test tool with no parameters."""

    return EmptyTool
