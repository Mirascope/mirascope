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
from openai.types.completion_usage import CompletionUsage
from openai.types.create_embedding_response import CreateEmbeddingResponse, Usage
from openai.types.embedding import Embedding
from pydantic import BaseModel, Field

from mirascope.openai.embedders import OpenAIEmbedder
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import OpenAIEmbeddingParams


@pytest.fixture()
def fixture_chat_completion_no_usage() -> ChatCompletion:
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
        model="gpt-4",
        object="chat.completion",
        usage=None,
    )


@pytest.fixture()
def fixture_chat_completion_with_tools_json_mode(
    fixture_chat_completion: ChatCompletion,
) -> ChatCompletion:
    """Returns a chat completion with a JSON mode tool call."""
    fixture_chat_completion.choices[
        0
    ].message.content = '{\n  "param": "param",\n  "optional": 0}'
    return fixture_chat_completion


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

    def my_openai_tool(param: str, optional: int = 0):
        """A test function."""

    return my_openai_tool


@pytest.fixture()
def fixture_chat_completion_with_tools_bad_stop_sequence(
    fixture_chat_completion_with_tools: ChatCompletion,
) -> ChatCompletion:
    """Returns a chat completion with tool calls but a bad stop sequence."""
    fixture_chat_completion_with_tools.choices[0].finish_reason = "length"
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
                                name="my_openai_tool",
                            ),
                            type="function",
                        )
                    ],
                ),
                **{"logprobs": None},
            ),
        ],
        created=0,
        model="gpt-4",
        object="chat.completion",
        usage=CompletionUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
    )


@pytest.fixture()
def fixture_chat_completion_chunk(
    fixture_chat_completion_chunks,
) -> ChatCompletionChunk:
    """Returns a chat completion chunk."""
    return fixture_chat_completion_chunks[0]


@pytest.fixture()
def fixture_chat_completion_last_chunk(
    fixture_chat_completion_chunks,
) -> ChatCompletionChunk:
    """Returns a chat completion last chunk."""
    return fixture_chat_completion_chunks[-1]


@pytest.fixture()
def fixture_chat_completion_chunks_with_tools() -> list[ChatCompletionChunk]:
    """Returns a list of chat completion chunks with tool calls."""

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
                                    arguments="", name="my_openai_tool"
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
                                id=None,
                                function=ChoiceDeltaToolCallFunction(
                                    arguments="", name=None
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
                                id=None,
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
                                id=None,
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
    fixture_chat_completion_chunks_with_tools: list[ChatCompletionChunk],
) -> ChatCompletionChunk:
    """Returns a chat completion chunk with tool calls."""
    return fixture_chat_completion_chunks_with_tools[0]


@pytest.fixture()
def fixture_chat_completion_last_chunk_with_tools(
    fixture_chat_completion_chunks_with_tools: list[ChatCompletionChunk],
) -> ChatCompletionChunk:
    """Returns a chat completion last chunk with tool calls."""
    return fixture_chat_completion_chunks_with_tools[-1]


@pytest.fixture()
def fixture_chat_completion_chunk_with_bad_tools(
    fixture_chat_completion_chunk_with_tools: ChatCompletionChunk,
) -> ChatCompletionChunk:
    """Returns a chat completion chunk with tool calls."""
    chunk = fixture_chat_completion_chunk_with_tools.model_copy()
    chunk.choices[0].delta.tool_calls[
        0
    ].function.arguments = '{\n  "param": 0,\n  "optional": 0}'  # type: ignore
    return chunk


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


@pytest.fixture()
def fixture_embeddings() -> CreateEmbeddingResponse:
    return CreateEmbeddingResponse(
        data=[
            Embedding(
                embedding=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                index=0,
                object="embedding",
            )
        ],
        model="test_model",
        object="list",
        usage=Usage(
            prompt_tokens=1,
            total_tokens=1,
        ),
    )


@pytest.fixture()
def fixture_openai_test_embedder():
    """Returns an `OpenAIEmbedding` instance."""

    class TestEmbedder(OpenAIEmbedder):
        api_key = "test"
        embedding_params = OpenAIEmbeddingParams(model="test_model")

    return TestEmbedder()


@pytest.fixture()
def fixture_openai_test_embedder_no_batch():
    """Returns an `OpenAIEmbedding` instance with no batching."""

    class TestEmbedder(OpenAIEmbedder):
        api_key = "test"
        embedding_params = OpenAIEmbeddingParams(model="test_model")

    return TestEmbedder(embed_batch_size=None)
