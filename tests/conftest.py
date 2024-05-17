"""Test configuration fixtures used across various modules."""
from contextlib import asynccontextmanager, contextmanager
from typing import Type

import pytest
from anthropic.types import (
    ContentBlock,
    ContentBlockDeltaEvent,
    TextDelta,
    Usage,
)
from anthropic.types.beta.tools import ToolsBetaMessage, ToolUseBlock
from cohere import StreamedChatResponse_TextGeneration
from cohere.types import (
    ApiMeta,
    ApiMetaBilledUnits,
    ChatCitation,
    ChatSearchQuery,
    ChatSearchResult,
    ChatSearchResultConnector,
    NonStreamedChatResponse,
    ToolCall,
)
from google.ai.generativelanguage import (
    Candidate,
    Content,
    GenerateContentResponse,
    Part,
)
from google.generativeai.types import (  # type: ignore
    GenerateContentResponse as GenerateContentResponseType,
)
from groq.lib.chat_completion_chunk import (
    ChatCompletionChunk,
    ChoiceDelta,
)
from groq.lib.chat_completion_chunk import Choice as ChunkChoice
from groq.lib.chat_completion_chunk import (
    ChoiceLogprobs as ChunkChoiceLogprobs,
)
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from openai.types.completion_usage import CompletionUsage
from pydantic import BaseModel, Field

from mirascope.anthropic import AnthropicTool
from mirascope.base import tool_fn
from mirascope.base.types import BaseConfig
from mirascope.openai import OpenAITool
from mirascope.openai.calls import OpenAICall
from mirascope.openai.types import OpenAICallParams


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
        model="gpt-4",
        object="chat.completion",
        usage=CompletionUsage(completion_tokens=0, prompt_tokens=0, total_tokens=0),
    )


@pytest.fixture()
def fixture_chat_completion_with_tools() -> ChatCompletion:
    """Returns a chat completion with tool calls."""
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
                                arguments='{\n  "param": "param",\n  "optional": 0}',
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
        usage=CompletionUsage(completion_tokens=0, prompt_tokens=0, total_tokens=0),
    )


@pytest.fixture()
def fixture_chat_completion_with_assistant_message_tool(
    fixture_chat_completion: ChatCompletion,
) -> ChatCompletion:
    """Returns a chat completion with an assistant message tool response."""
    fixture_chat_completion_copy = fixture_chat_completion.model_copy()
    fixture_chat_completion_copy.choices[
        0
    ].message.content = '{\n  "param": "param",\n  "optional": 0}'
    return fixture_chat_completion_copy


@tool_fn(lambda param, optional: "test")
class MyOpenAITool(OpenAITool):
    """A test tool."""

    param: str = Field(..., description="A test parameter.")
    optional: int = 0


@pytest.fixture()
def fixture_my_openai_tool_instance(
    fixture_my_openai_tool: Type[MyOpenAITool],
) -> MyOpenAITool:
    """Returns an instance of `MyTool`."""
    return fixture_my_openai_tool(
        param="param",
        optional=0,
        tool_call=ChatCompletionMessageToolCall(
            id="id",
            function=Function(
                arguments=('{\n  "param": "param",\n  "optional": 0}'),
                name="MyOpenAITool",
            ),
            type="function",
        ),
    )


@pytest.fixture()
def fixture_my_openai_tool_schema_instance(
    fixture_my_openai_tool_schema: Type[BaseModel],
) -> BaseModel:
    """Returns an instance of the `MyOpenAITool` schema `BaseModel`."""
    return fixture_my_openai_tool_schema(param="param", optional=0)


@pytest.fixture()
def fixture_my_openai_tool() -> Type[MyOpenAITool]:
    """Returns a `MyOpenAITool` class."""
    return MyOpenAITool


@pytest.fixture()
def fixture_my_openai_tool_schema() -> Type[BaseModel]:
    """Returns a `MyOpenAITool` schema `BaseModel`."""

    class MyOpenAITool(BaseModel):
        """A test tool."""

        param: str = Field(..., description="A test parameter.")
        optional: int = 0

    return MyOpenAITool


@pytest.fixture()
def fixture_chat_search_query() -> ChatSearchQuery:
    """Returns a Cohere chat search query."""
    return ChatSearchQuery(text="test query", generation_id="id")


@pytest.fixture()
def fixture_chat_search_result(
    fixture_chat_search_query: ChatSearchQuery,
) -> ChatSearchResult:
    """Returns a Cohere chat search result."""
    return ChatSearchResult(
        search_query=fixture_chat_search_query,
        connector=ChatSearchResultConnector(id="id"),
        document_ids=["test_id"],
    )


@pytest.fixture()
def fixture_chat_document() -> dict[str, str]:
    """Returns a Cohere chat document."""
    return {"id": "test_doc_id", "text": "test doc"}


@pytest.fixture()
def fixture_chat_citation() -> ChatCitation:
    """Returns a Cohere chat citation."""
    return ChatCitation(start=0, end=0, text="", document_ids=["test_cite_id"])


@pytest.fixture()
def fixture_tool_call() -> ToolCall:
    """Returns a Cohere tool call."""
    return ToolCall(
        name="BookTool",
        parameters={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
    )


@pytest.fixture()
def fixture_non_streamed_response(
    fixture_chat_search_query: ChatSearchQuery,
    fixture_chat_search_result: ChatSearchResult,
    fixture_chat_document: dict[str, str],
    fixture_chat_citation: ChatCitation,
    fixture_tool_call: ToolCall,
) -> NonStreamedChatResponse:
    """Returns a Cohere chat response."""
    return NonStreamedChatResponse(
        text="Test response",
        search_queries=[fixture_chat_search_query],
        search_results=[fixture_chat_search_result],
        documents=[fixture_chat_document],
        citations=[fixture_chat_citation],
        tool_calls=[fixture_tool_call],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_non_streamed_response_no_usage(
    fixture_chat_search_query: ChatSearchQuery,
    fixture_chat_search_result: ChatSearchResult,
    fixture_chat_document: dict[str, str],
    fixture_chat_citation: ChatCitation,
    fixture_tool_call: ToolCall,
) -> NonStreamedChatResponse:
    """Returns a Cohere chat response."""
    return NonStreamedChatResponse(
        text="Test response",
        search_queries=[fixture_chat_search_query],
        search_results=[fixture_chat_search_result],
        documents=[fixture_chat_document],
        citations=[fixture_chat_citation],
        tool_calls=[fixture_tool_call],
        meta=None,
    )


@pytest.fixture()
def fixture_cohere_response_chunk():
    """Returns a Cohere chat response chunk."""
    return StreamedChatResponse_TextGeneration(
        event_type="text-generation",
        text="test",
        search_queries=None,
        search_results=None,
        documents=None,
        citations=None,
        tool_calls=None,
        response=None,
    )


@pytest.fixture()
def fixture_cohere_response_chunks(
    fixture_cohere_response_chunk: StreamedChatResponse_TextGeneration,
):
    """Returns a context managed stream."""
    return [fixture_cohere_response_chunk] * 3


@pytest.fixture()
def fixture_cohere_async_response_chunks(
    fixture_cohere_response_chunk: StreamedChatResponse_TextGeneration,
):
    """Returns a context managed async stream"""

    async def generator():
        yield fixture_cohere_response_chunk

    return generator()


@pytest.fixture()
def fixture_anthropic_message_chunk():
    """Returns an Anthropic message."""
    return ContentBlockDeltaEvent(
        delta=TextDelta(text="test", type="text_delta"),
        index=1,
        type="content_block_delta",
    )


@pytest.fixture()
def fixture_anthropic_message_chunks(
    fixture_anthropic_message_chunk,
):
    """Returns a context managed stream."""

    @contextmanager
    def chunks():
        yield [fixture_anthropic_message_chunk] * 3

    return chunks()


@pytest.fixture()
def fixture_anthropic_async_message_chunks(fixture_anthropic_message_chunk):
    """Returns a context managed async stream"""

    async def generator():
        yield fixture_anthropic_message_chunk

    @asynccontextmanager
    async def async_chunks():
        yield generator()

    return async_chunks()


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
def fixture_generate_content_response():
    """Returns a `GenerateContentResponse` instance."""
    return GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    content=Content(
                        parts=[Part(text="Who is the author?")], role="model"
                    )
                )
            ]
        )
    )


@pytest.fixture()
def fixture_anthropic_message_with_tools() -> ToolsBetaMessage:
    """Returns an Anthropic message with tools XML in the response"""
    return ToolsBetaMessage(
        id="0",
        content=[
            ContentBlock(type="text", text="test"),
            ToolUseBlock(
                id="test",
                name="AnthropicBookTool",
                input={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
                type="tool_use",
            ),
        ],
        model="test",
        role="assistant",
        type="message",
        usage=Usage(input_tokens=0, output_tokens=0),
        stop_reason="tool_use",
    )


class AnthropicBookTool(AnthropicTool):
    title: str
    author: str


@pytest.fixture()
def fixture_anthropic_book_tool() -> Type[AnthropicBookTool]:
    """Returns the `AnthropicBookTool` type definition."""

    return AnthropicBookTool


@pytest.fixture(scope="function")
def fixture_openai_test_call():
    """Returns an `OpenAICall` instance."""

    class OpenAITestCall(OpenAICall):
        prompt_template = """\
            SYSTEM: This is a test.
            USER: You are being tested.
        """
        api_key = "test"

        call_params = OpenAICallParams(model="gpt-4")
        configuration = BaseConfig(client_wrappers=[], llm_ops=[])

    return OpenAITestCall()
