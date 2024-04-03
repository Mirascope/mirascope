"""Configuration for the Mirascope openai module tests."""
from typing import Callable, Type

import pytest
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
)
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
from pydantic import BaseModel, Field

from mirascope.openai.calls import OpenAICall
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import OpenAICallParams


@pytest.fixture()
def fixture_my_schema() -> Type[BaseModel]:
    """Returns a `MySchema` class type."""

    class MySchema(BaseModel):
        """A test schema."""

        param: str = Field(..., description="A test parameter.")
        optional: int = 0

    return MySchema


class EmptyOpenAITool(OpenAITool):
    """A test tool with no parameters."""


@pytest.fixture()
def fixture_empty_openai_tool() -> Type[EmptyOpenAITool]:
    """Returns an `EmptyOpenAITool` class."""
    return EmptyOpenAITool


@pytest.fixture()
def fixture_my_openai_tool_function() -> Callable:
    """Returns a function version of `MyOpenAITool`."""

    def my_open_a_i_tool(param: str, optional: int = 0):
        """A test function."""

    return my_open_a_i_tool


@pytest.fixture()
def fixture_chat_compmletion_with_tools_bad_stop_sequence(
    fixture_chat_completion_with_tools: ChatCompletion,
) -> ChatCompletion:
    """Returns a chat completion with tool calls but a bad stop sequence."""
    fixture_chat_completion_with_tools.choices[0].finish_reason = "stop"
    return fixture_chat_completion_with_tools


@pytest.fixture()
def fixture_chat_completion_with_bad_tools() -> ChatCompletion:
    """Returns a chat completion with tool calls that don't match the tool's schema."""
    return ChatCompletion(
        id="test_id",
        choices=[
            Choice(
                finish_reason="tool_calls",
                index=0,
                message=ChatCompletionMessage(
                    role="assistant",
                    tool_calls=[
                        ChatCompletionMessageToolCall(
                            id="id",
                            function=Function(
                                arguments=('{\n  "param": 0,\n  "optional": 0}'),
                                name="MyOpenAITool",
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
def fixture_chat_completion_chunks() -> list[ChatCompletionChunk]:
    """Returns chat completion chunks."""
    return [
        ChatCompletionChunk(
            id="test_id",
            choices=[
                ChunkChoice(
                    **{"logprobs": None},
                    delta=ChoiceDelta(content="I'm"),
                    finish_reason="stop",
                    index=0,
                ),
            ],
            created=0,
            model="test_model",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="test_id",
            choices=[
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
        ),
    ]


@pytest.fixture()
def fixture_chat_completion_chunk(
    fixture_chat_completion_chunks,
) -> ChatCompletionChunk:
    """Returns a chat completion chunk."""
    return fixture_chat_completion_chunks[0]


@pytest.fixture()
def fixture_chat_completion_chunks_with_tools(
    request: pytest.FixtureRequest,
) -> list[ChatCompletionChunk]:
    """Returns a list of chat completion chunks with tool calls."""
    try:
        name = request.param
    except AttributeError:
        name = None

    return [
        ChatCompletionChunk(
            id="test_id",
            choices=[
                ChunkChoice(
                    logprobs=None,
                    delta=ChoiceDelta(
                        tool_calls=[
                            ChoiceDeltaToolCall(
                                index=0,
                                id="id0",
                                function=ChoiceDeltaToolCallFunction(
                                    arguments="", name=name
                                ),
                                type="function",
                            )
                        ]
                    ),
                    index=0,
                ),
            ],
            created=0,
            model="test_model",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="test_id",
            choices=[
                ChunkChoice(
                    logprobs=None,
                    delta=ChoiceDelta(
                        tool_calls=[
                            ChoiceDeltaToolCall(
                                index=0,
                                id="id0",
                                function=ChoiceDeltaToolCallFunction(
                                    arguments='{\n "param": "param"', name=None
                                ),
                                type="function",
                            )
                        ]
                    ),
                    index=0,
                ),
            ],
            created=0,
            model="test_model",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="test_id",
            choices=[
                ChunkChoice(
                    logprobs=None,
                    delta=ChoiceDelta(
                        tool_calls=[
                            ChoiceDeltaToolCall(
                                index=0,
                                id="id0",
                                function=ChoiceDeltaToolCallFunction(
                                    arguments=',\n "optional": 0\n}', name=None
                                ),
                                type="function",
                            )
                        ]
                    ),
                    index=0,
                ),
            ],
            created=0,
            model="test_model",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="test_id",
            choices=[
                ChunkChoice(
                    logprobs=None,
                    delta=ChoiceDelta(tool_calls=None),
                    finish_reason="stop",
                    index=0,
                ),
            ],
            created=0,
            model="test_model",
            object="chat.completion.chunk",
        ),
    ]


@pytest.fixture()
def fixture_chat_completion_chunk_with_tools(
    fixture_chat_completion_chunks_with_tools,
) -> ChatCompletionChunk:
    """Returns a chat completion chunk with tool calls."""
    return fixture_chat_completion_chunks_with_tools[0]


@pytest.fixture()
def fixture_openai_test_call():
    """Returns an `OpenAICall` instance."""

    class OpenAITestCall(OpenAICall):
        prompt_template = """\
            SYSTEM: This is a test.
            USER: You are being tested.
        """
        api_key = "test"

        call_params = OpenAICallParams(model="gpt-4")

    return OpenAITestCall()


class Str(OpenAITool):
    """A wrapper tool for the base string type."""

    value: str


@pytest.fixture()
def fixture_str_tool() -> Type[Str]:
    """Returns the `Str` tool type."""
    return Str


@pytest.fixture()
def fixture_chat_completion_with_str_tool() -> ChatCompletion:
    """Returns a chat completion with a tool matching a string base type."""
    return ChatCompletion(
        id="test_id",
        choices=[
            Choice(
                finish_reason="tool_calls",
                index=0,
                message=ChatCompletionMessage(
                    role="assistant",
                    tool_calls=[
                        ChatCompletionMessageToolCall(
                            id="id",
                            function=Function(
                                arguments='{\n  "value": "value"}',
                                name="Str",
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
