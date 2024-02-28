"""Fixtures for repeated use in testing."""
from typing import Type

import pytest
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
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
from pydantic import Field

from mirascope.chat.tools import OpenAITool
from mirascope.cli.schemas import MirascopeSettings, VersionTextFile
from mirascope.prompts import OpenAICallParams

from .test_prompts import FooBarPrompt, MessagesPrompt, TagPrompt, TagsPrompt


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
def fixture_messages_prompt() -> MessagesPrompt:
    """Returns a `MessagesPrompt` instance."""
    return MessagesPrompt(foo="foo", bar="bar")


@pytest.fixture()
def fixture_tag_prompt() -> TagPrompt:
    """Returns a `TagPrompt` instance."""
    return TagPrompt()


@pytest.fixture()
def fixture_tags_prompt() -> TagsPrompt:
    """Returns a `TagPrompt` instance."""
    return TagsPrompt()


@pytest.fixture()
def fixture_expected_foobar_prompt_messages() -> list[ChatCompletionMessageParam]:
    """Returns the expected messages parsed from `FooBarPrompt`."""
    return [
        ChatCompletionUserMessageParam(
            role="user",
            content=(
                "This is a test prompt about foobar. "
                "This should be on the same line in the template."
                "\n    This should be indented on a new line in the template."
            ),
        )
    ]


@pytest.fixture()
def fixture_expected_messages_prompt_messages() -> list[ChatCompletionMessageParam]:
    """Returns the expected messages parsed from `MessagesPrompt`."""
    return [
        ChatCompletionSystemMessageParam(
            role="system",
            content=(
                "This is the system message about foo.\n    "
                "This is also the system message."
            ),
        ),
        ChatCompletionUserMessageParam(
            role="user", content="This is the user message about bar."
        ),
        ChatCompletionToolMessageParam(
            role="tool", content="This is the output of calling a tool."
        ),  # type: ignore
        ChatCompletionAssistantMessageParam(
            role="assistant",
            content=(
                "This is an assistant message about foobar. "
                "This is also part of the assistant message."
            ),
        ),
    ]


@pytest.fixture()
def fixture_string_prompt() -> str:
    """Returns a string prompt."""
    return "This is a test prompt."


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
def fixture_chat_completion_with_schema_tool() -> ChatCompletion:
    """Returns a chat completion with a tool matching a BaseModel schema."""
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
                                name="MySchemaTool",
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


class MyTool(OpenAITool):
    """A test tool."""

    param: str = Field(..., description="A test parameter.")
    optional: int = 0


class EmptyTool(OpenAITool):
    """A test tool with no parameters."""


@pytest.fixture()
def fixture_empty_tool() -> Type[OpenAITool]:
    """Returns an `EmptyTool` class."""
    return EmptyTool


class FooBarPromptWithMyTool(FooBarPrompt):
    __doc__ = FooBarPrompt.__doc__

    _call_params: OpenAICallParams = OpenAICallParams(
        model="gpt-3.5-turbo-1106", tools=[MyTool]
    )


@pytest.fixture()
def fixture_foobar_prompt_with_my_tool() -> FooBarPromptWithMyTool:
    """Returns a `FooBarPromptWithTools` instance."""
    return FooBarPromptWithMyTool(foo="foo", bar="bar")


class FooBarPromptWithMyToolAndEmptyTool(FooBarPrompt):
    __doc__ = FooBarPrompt.__doc__

    _call_params: OpenAICallParams = OpenAICallParams(
        model="gpt-3.5-turbo-1106", tools=[MyTool, EmptyTool]
    )


@pytest.fixture()
def fixture_foobar_prompt_with_my_tool_and_empty_tool() -> (
    FooBarPromptWithMyToolAndEmptyTool
):
    """Returns a `FooBarPromptWithTools` instance."""
    return FooBarPromptWithMyToolAndEmptyTool(foo="foo", bar="bar")


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
                arguments=('{\n  "param": "param",\n  "optional": 0}'),
                name="MyTool",
            ),
            type="function",
        ),
    )


@pytest.fixture()
def fixture_mirascope_user_settings() -> MirascopeSettings:
    """Returns a `MirascopeSettings` instance."""
    return MirascopeSettings(
        format_command="ruff check --select I --fix; ruff format",
        mirascope_location=".mirascope",
        prompts_location="prompts",
        version_file_name="version.txt",
        versions_location=".mirascope/versions",
        auto_tag=True,
    )


@pytest.fixture
def fixture_prompt_versions() -> VersionTextFile:
    """Returns a `VersionTextFile` instance."""
    return VersionTextFile(current_revision="0002", latest_revision="0002")
