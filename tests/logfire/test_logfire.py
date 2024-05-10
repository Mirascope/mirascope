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
from mirascope.cohere.embedders import CohereEmbedder
from mirascope.cohere.types import CohereCallParams
from mirascope.gemini.calls import GeminiCall
from mirascope.groq.calls import GroqCall
from mirascope.logfire import with_logfire
from mirascope.openai import OpenAICall, OpenAIEmbedder, OpenAIExtractor
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import OpenAICallResponse
from mirascope.rag.embedders import BaseEmbedder
from mirascope.rag.types import Document

logfire.configure(send_to_logfire=False)

os.environ["OPENAI_API_KEY"] = "test"


class MyCall(OpenAICall):
    prompt_template = "test"


@with_logfire
class MyNestedCall(MyCall):
    ...


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_call_with_logfire(
    mock_create: MagicMock, fixture_chat_completion: ChatCompletion
) -> None:
    mock_create.return_value = fixture_chat_completion
    my_call = MyNestedCall()
    my_call.call()
    my_call.stream()
    assert my_call.call_params.logfire is not None


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
    assert my_call.call_params.logfire is not None


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
    assert my_call.call_params.logfire is not None


@with_logfire
class CohereTempCall(CohereCall):
    prompt_template = ""
    api_key = "test"
    call_params = CohereCallParams(preamble="test")


@patch("cohere.Client.chat", new_callable=MagicMock)
def test_cohere_call_call_with_logfire(
    mock_chat: MagicMock,
    fixture_non_streamed_response: NonStreamedChatResponse,
) -> None:
    """Tests that `CohereCall.call` returns the expected response with logfire."""
    mock_chat.return_value = fixture_non_streamed_response
    my_call = CohereTempCall()
    my_call.call()
    assert my_call.call_params.logfire is not None


@patch("cohere.AsyncClient.chat", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_cohere_call_call_async_with_logfire(
    mock_chat: AsyncMock,
    fixture_non_streamed_response: NonStreamedChatResponse,
) -> None:
    """Tests that `CohereCall.call_async` returns the expected response with logfire."""
    mock_chat.return_value = fixture_non_streamed_response

    my_call = CohereTempCall()
    await my_call.call_async()
    assert my_call.call_params.logfire is not None


@patch("cohere.Client.chat_stream", new_callable=MagicMock)
def test_cohere_call_stream_with_logfire(
    mock_chat_stream: MagicMock,
    fixture_cohere_response_chunks: list[StreamedChatResponse],
) -> None:
    """Tests that `CohereCall.stream` returns the expected response with logfire."""
    mock_chat_stream.return_value = fixture_cohere_response_chunks
    mock_chat_stream.__name__ = "stream"
    my_call = CohereTempCall()
    chunks = [chunk for chunk in my_call.stream()]
    for chunk in chunks:
        assert isinstance(chunk.chunk, StreamedChatResponse_TextGeneration)
    assert my_call.call_params.logfire is not None


@patch("cohere.AsyncClient.chat_stream", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_cohere_call_stream_async_with_logfire(
    mock_chat_stream: MagicMock,
    fixture_cohere_async_response_chunks,
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
    assert my_call.call_params.logfire_async is not None


@patch(
    "anthropic.resources.messages.Messages.stream",
    new_callable=MagicMock,
)
def test_anthropic_call_stream(
    mock_stream: MagicMock,
    fixture_anthropic_message_chunks: ContextManager[list],
    fixture_anthropic_test_call_with_logfire: type[AnthropicCall],
):
    """Tests `AnthropicPrompt.stream` returns the expected response when called."""
    mock_stream.return_value = fixture_anthropic_message_chunks
    mock_stream.__name__ = "stream"

    my_call = fixture_anthropic_test_call_with_logfire()
    stream = my_call.stream()
    for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
    assert my_call.call_params.logfire is not None


@patch(
    "anthropic.resources.messages.AsyncMessages.stream",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_anthropic_call_stream_async(
    mock_stream: MagicMock,
    fixture_anthropic_async_message_chunks: AsyncContextManager[list],
    fixture_anthropic_test_call_with_logfire: type[AnthropicCall],
):
    """Tests `AnthropicPrompt.stream_async` returns the expected response when called."""
    mock_stream.return_value = fixture_anthropic_async_message_chunks
    mock_stream.__name__ = "stream"

    my_call = fixture_anthropic_test_call_with_logfire()
    stream = my_call.stream_async()
    async for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
    assert my_call.call_params.logfire_async is not None


@patch(
    "groq.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_groq_call_stream_async(
    mock_create: AsyncMock,
    fixture_chat_completion_stream_response: list[ChatCompletionChunk],
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

    assert my_call.call_params.logfire_async is not None


@patch("mirascope.openai.calls.OpenAICall.call", new_callable=MagicMock)
def test_extractor_with_logfire(
    mock_call: MagicMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: type[OpenAITool],
    fixture_my_openai_tool_schema: type[BaseModel],
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

        extract_schema: type[BaseModel] = fixture_my_openai_tool_schema

    my_extractor = TempExtractor()
    my_extractor.extract()
    assert my_extractor.call_params.logfire is not None


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
):
    """Test the add method of the ChromaVectorStore class with documents as argument"""
    mock_upsert.return_value = None
    my_vectorstore = VectorStore()
    my_vectorstore.add([Document(text="foo", id="1")])
    mock_upsert.assert_called_once_with(ids=["1"], documents=["foo"])
    assert my_vectorstore.vectorstore_params.logfire is not None


@patch("chromadb.api.models.Collection.Collection.query")
def test_chroma_vectorstore_retrieve(
    mock_query: MagicMock,
):
    """Test the retrieve method of the ChromaVectorStore class."""
    mock_query.return_value = ChromaQueryResult(ids=[["1"]])
    my_vectorstore = VectorStore()
    my_vectorstore.retrieve("test")
    mock_query.assert_called_once_with(query_texts=["test"])
    assert my_vectorstore.vectorstore_params.logfire is not None


def test_openai_embedder_with_logfire() -> None:
    @with_logfire
    class MyEmbedder(OpenAIEmbedder):
        ...

    my_embedder = MyEmbedder()
    assert my_embedder.embedding_params.logfire is not None


def test_cohere_embedder_with_logfire() -> None:
    @with_logfire
    class MyOtherEmbedder(CohereEmbedder):
        ...

    my_embedder = MyOtherEmbedder()
    assert my_embedder.embedding_params.logfire is not None
