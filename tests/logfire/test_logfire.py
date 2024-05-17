"""Tests for the Mirascope + Logfire integration."""
import os
from typing import AsyncContextManager, ContextManager
from unittest.mock import AsyncMock, MagicMock, patch

import logfire
import pytest
from anthropic.types import Message
from cohere import StreamedChatResponse_TextGeneration
from cohere.types import NonStreamedChatResponse, StreamedChatResponse
from google.ai.generativelanguage import GenerateContentResponse
from groq.lib.chat_completion_chunk import ChatCompletionChunk
from logfire.testing import CaptureLogfire
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from mirascope.anthropic.calls import AnthropicCall
from mirascope.anthropic.tools import AnthropicTool
from mirascope.anthropic.types import AnthropicCallParams, AnthropicCallResponseChunk
from mirascope.chroma.types import ChromaQueryResult, ChromaSettings
from mirascope.chroma.vectorstores import ChromaVectorStore
from mirascope.cohere.calls import CohereCall
from mirascope.cohere.types import CohereCallParams
from mirascope.gemini.calls import GeminiCall
from mirascope.groq.calls import GroqCall
from mirascope.logfire import with_logfire
from mirascope.openai import OpenAICall, OpenAIExtractor
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import OpenAICallParams, OpenAICallResponse
from mirascope.rag.embedders import BaseEmbedder
from mirascope.rag.types import Document

logfire.configure(send_to_logfire=False)

os.environ["OPENAI_API_KEY"] = "test"

openai_model = "gpt-3.5-turbo"


class MyCall(OpenAICall):
    ...


@with_logfire
class MyNestedCall(MyCall):
    prompt_template = "test"

    call_params = OpenAICallParams(model=openai_model)


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_call_with_logfire(
    mock_create: MagicMock,
    fixture_chat_completion: ChatCompletion,
    capfire: CaptureLogfire,
) -> None:
    mock_create.return_value = fixture_chat_completion
    mock_create.__name__ = "call"
    my_call = MyNestedCall()
    my_call.call()
    my_call.stream()
    exporter = capfire.exporter
    # TODO: Figure out why instrument_openai doesn't show up in CaptureLogfire
    expected_span_names = [
        "MyNestedCall.call (pending)",
        "MyNestedCall.call",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    assert span_names == expected_span_names


@patch(
    "anthropic.resources.beta.tools.messages.AsyncMessages.create",
    new_callable=AsyncMock,
)
@patch(
    "anthropic.resources.beta.tools.messages.Messages.create",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_tool_call_with_logfire(
    mock_create: MagicMock,
    mock_create_async: AsyncMock,
    fixture_anthropic_book_tool: type[AnthropicTool],
    fixture_anthropic_message_with_tools: Message,
    capfire: CaptureLogfire,
) -> None:
    mock_create.return_value = fixture_anthropic_message_with_tools
    mock_create.__name__ = "mock_create"
    mock_create_async.return_value = fixture_anthropic_message_with_tools
    mock_create_async.__name__ = "mock_create_async"

    @with_logfire
    class MyAnthropicCall(AnthropicCall):
        prompt_template = "test"
        api_key = "test"

        call_params = AnthropicCallParams(tools=[fixture_anthropic_book_tool])

    my_call = MyAnthropicCall()
    my_call.call()
    await my_call.call_async()
    exporter = capfire.exporter
    expected_span_names = [
        "MyAnthropicCall.call (pending)",
        "anthropic.mock_create with claude-3-haiku-20240307 (pending)",
        "anthropic.mock_create with claude-3-haiku-20240307",
        "MyAnthropicCall.call",
        "MyAnthropicCall.call_async (pending)",
        "anthropic.mock_create_async with claude-3-haiku-20240307 (pending)",
        "anthropic.mock_create_async with claude-3-haiku-20240307",
        "MyAnthropicCall.call_async",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    print(span_names)
    assert span_names == expected_span_names


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_gemini_call_call(
    mock_generate_content: MagicMock,
    fixture_generate_content_response: GenerateContentResponse,
    capfire: CaptureLogfire,
) -> None:
    """Tests that `GeminiClass.call` returns the expected response."""
    mock_generate_content.return_value = fixture_generate_content_response
    mock_generate_content.__name__ = "call"

    @with_logfire
    class MyGeminiCall(GeminiCall):
        ...

    my_call = MyGeminiCall()
    my_call.call()
    exporter = capfire.exporter
    expected_span_names = [
        "MyGeminiCall.call (pending)",
        "gemini.call with gemini-1.0-pro (pending)",
        "gemini.call with gemini-1.0-pro",
        "MyGeminiCall.call",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    assert span_names == expected_span_names


@with_logfire
class CohereTempCall(CohereCall):
    prompt_template = ""
    api_key = "test"
    call_params = CohereCallParams(preamble="test")


@patch("cohere.Client.chat", new_callable=MagicMock)
def test_cohere_call_call_with_logfire(
    mock_chat: MagicMock,
    fixture_non_streamed_response: NonStreamedChatResponse,
    capfire: CaptureLogfire,
) -> None:
    """Tests that `CohereCall.call` returns the expected response with logfire."""
    mock_chat.return_value = fixture_non_streamed_response
    my_call = CohereTempCall()
    my_call.call()
    exporter = capfire.exporter
    expected_span_names = [
        "CohereTempCall.call (pending)",
        "cohere.wrapped with command-r-plus (pending)",
        "cohere.wrapped with command-r-plus",
        "CohereTempCall.call",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    assert span_names == expected_span_names


@patch("cohere.AsyncClient.chat", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_cohere_call_call_async_with_logfire(
    mock_chat: AsyncMock,
    fixture_non_streamed_response: NonStreamedChatResponse,
    capfire: CaptureLogfire,
) -> None:
    """Tests that `CohereCall.call_async` returns the expected response with logfire."""
    mock_chat.return_value = fixture_non_streamed_response

    my_call = CohereTempCall()
    await my_call.call_async()
    exporter = capfire.exporter
    expected_span_names = [
        "CohereTempCall.call_async (pending)",
        "cohere.wrapped with command-r-plus (pending)",
        "cohere.wrapped with command-r-plus",
        "CohereTempCall.call_async",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    assert span_names == expected_span_names


@patch("cohere.Client.chat_stream", new_callable=MagicMock)
def test_cohere_call_stream_with_logfire(
    mock_chat_stream: MagicMock,
    fixture_cohere_response_chunks: list[StreamedChatResponse],
    capfire: CaptureLogfire,
) -> None:
    """Tests that `CohereCall.stream` returns the expected response with logfire."""
    mock_chat_stream.return_value = fixture_cohere_response_chunks
    mock_chat_stream.__name__ = "stream"
    my_call = CohereTempCall()
    chunks = [chunk for chunk in my_call.stream()]
    for chunk in chunks:
        assert isinstance(chunk.chunk, StreamedChatResponse_TextGeneration)
    exporter = capfire.exporter
    expected_span_names = [
        "CohereTempCall.stream (pending)",
        "streaming response from {request_data[model]!r} took {duration:.2f}s",
        "CohereTempCall.stream",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    assert span_names == expected_span_names


@patch("cohere.AsyncClient.chat_stream", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_cohere_call_stream_async_with_logfire(
    mock_chat_stream: MagicMock,
    fixture_cohere_async_response_chunks,
    capfire: CaptureLogfire,
):
    """Tests `CohereCall.stream_async` returns expected response with logfire."""

    @with_logfire
    class TempCall(CohereCall):
        prompt_template = ""
        api_key = "test"

    mock_chat_stream.return_value = fixture_cohere_async_response_chunks
    mock_chat_stream.__name__ = "stream"
    my_call = TempCall()
    stream = my_call.stream_async()

    async for chunk in stream:
        assert isinstance(chunk.chunk, StreamedChatResponse_TextGeneration)
    exporter = capfire.exporter
    expected_span_names = [
        "TempCall.stream_async (pending)",
        "streaming response from {request_data[model]!r} took {duration:.2f}s",
        "TempCall.stream_async",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    assert span_names == expected_span_names


@patch(
    "anthropic.resources.messages.Messages.stream",
    new_callable=MagicMock,
)
def test_anthropic_call_stream(
    mock_stream: MagicMock,
    fixture_anthropic_message_chunks: ContextManager[list],
    fixture_anthropic_test_call_with_logfire: type[AnthropicCall],
    capfire: CaptureLogfire,
):
    """Tests `AnthropicPrompt.stream` returns the expected response when called."""
    mock_stream.return_value = fixture_anthropic_message_chunks
    mock_stream.__name__ = "stream"

    my_call = fixture_anthropic_test_call_with_logfire()
    stream = my_call.stream()
    for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
    exporter = capfire.exporter
    expected_span_names = [
        "AnthropicLogfireCall.stream (pending)",
        "streaming response from {request_data[model]!r} took {duration:.2f}s",
        "AnthropicLogfireCall.stream",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    assert span_names == expected_span_names


@patch(
    "anthropic.resources.messages.AsyncMessages.stream",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_anthropic_call_stream_async(
    mock_stream: MagicMock,
    fixture_anthropic_async_message_chunks: AsyncContextManager[list],
    fixture_anthropic_test_call_with_logfire: type[AnthropicCall],
    capfire: CaptureLogfire,
):
    """Tests `AnthropicPrompt.stream_async` returns the expected response when called."""
    mock_stream.return_value = fixture_anthropic_async_message_chunks
    mock_stream.__name__ = "stream"

    my_call = fixture_anthropic_test_call_with_logfire()
    stream = my_call.stream_async()
    async for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
    exporter = capfire.exporter
    expected_span_names = [
        "AnthropicLogfireCall.stream_async (pending)",
        "streaming response from {request_data[model]!r} took {duration:.2f}s",
        "AnthropicLogfireCall.stream_async",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    assert span_names == expected_span_names


@patch(
    "groq.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_groq_call_stream_async(
    mock_create: AsyncMock,
    fixture_chat_completion_stream_response: list[ChatCompletionChunk],
    capfire: CaptureLogfire,
):
    """Tests `GroqCall.stream_async` returns expected response with logfire."""

    @with_logfire
    class TempCall(GroqCall):
        prompt_template = ""
        api_key = "test"

    mock_create.return_value.__aiter__.return_value = (
        fixture_chat_completion_stream_response
    )
    mock_create.__name__ = "stream"
    my_call = TempCall()
    stream = my_call.stream_async()

    i = 0
    async for chunk in stream:
        assert chunk.chunk == fixture_chat_completion_stream_response[i]
        i += 1

    exporter = capfire.exporter
    expected_span_names = [
        "TempCall.stream_async (pending)",
        "streaming response from {request_data[model]!r} took {duration:.2f}s",
        "TempCall.stream_async",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    assert span_names == expected_span_names


@patch("mirascope.openai.calls.OpenAICall.call", new_callable=MagicMock)
def test_extractor_with_logfire(
    mock_call: MagicMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: type[OpenAITool],
    fixture_my_openai_tool_schema: type[BaseModel],
    capfire: CaptureLogfire,
) -> None:
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_tools,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )

    @with_logfire
    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"
        call_params = OpenAICallParams(model=openai_model)
        extract_schema: type[BaseModel] = fixture_my_openai_tool_schema

    my_extractor = TempExtractor()
    my_extractor.extract()
    exporter = capfire.exporter
    expected_span_names = [
        "TempExtractor.extract (pending)",
        # TODO: Figure out why this is not in the span, works fine outside test
        # f"Chat Completion with '{openai_model}'",
        "TempExtractor.extract",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    print(span_names)
    assert span_names == expected_span_names


class MyEmbedder(BaseEmbedder):
    def embed(self, input: list[str]) -> list[str]:
        return input  # pragma: no cover

    async def embed_async(self, input: list[str]) -> list[str]:
        return input  # pragma: no cover

    def __call__(self, input: str) -> list[float]:
        return [1, 2, 3]  # pragma: no cover


@with_logfire
class VectorStore(ChromaVectorStore):
    index_name = "test"
    client_settings = ChromaSettings(mode="ephemeral")
    embedder = MyEmbedder()


@patch("chromadb.api.models.Collection.Collection.upsert")
def test_chroma_vectorstore_add_document(
    mock_upsert: MagicMock,
    capfire: CaptureLogfire,
):
    """Test the add method of the ChromaVectorStore class with documents as argument"""
    mock_upsert.return_value = None
    my_vectorstore = VectorStore()
    my_vectorstore.add([Document(text="foo", id="1")])
    mock_upsert.assert_called_once_with(ids=["1"], documents=["foo"])
    exporter = capfire.exporter
    expected_span_names = [
        "VectorStore.add (pending)",
        "VectorStore.add",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    assert span_names == expected_span_names


@patch("chromadb.api.models.Collection.Collection.query")
def test_chroma_vectorstore_retrieve(
    mock_query: MagicMock,
    capfire: CaptureLogfire,
):
    """Test the retrieve method of the ChromaVectorStore class."""
    mock_query.return_value = ChromaQueryResult(ids=[["1"]])
    my_vectorstore = VectorStore()
    my_vectorstore.retrieve("test")
    mock_query.assert_called_once_with(query_texts=["test"])
    exporter = capfire.exporter
    expected_span_names = [
        "VectorStore.retrieve (pending)",
        "VectorStore.retrieve",
    ]
    span_names = [span.name for span in exporter.exported_spans]
    assert span_names == expected_span_names
