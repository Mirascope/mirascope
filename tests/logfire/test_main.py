"""Tests for the Mirascope + Logfire integration."""
import os
from typing import Any, AsyncContextManager, AsyncGenerator, ContextManager
from unittest.mock import AsyncMock, MagicMock, patch

import logfire
import pytest
from cohere import StreamedChatResponse_TextGeneration
from cohere.types import NonStreamedChatResponse, StreamedChatResponse
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from mirascope.anthropic.calls import AnthropicCall
from mirascope.anthropic.types import AnthropicCallResponseChunk
from mirascope.chroma.vectorstores import ChromaVectorStore
from mirascope.cohere.calls import CohereCall
from mirascope.cohere.embedders import CohereEmbedder
from mirascope.cohere.types import CohereCallParams
from mirascope.logfire import with_logfire
from mirascope.openai import OpenAICall, OpenAIEmbedder, OpenAIExtractor
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import OpenAICallResponse
from mirascope.rag.chunkers import TextChunker

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


@patch("cohere.AsyncClient.chat_stream", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_cohere_call_stream_async_with_logfire(
    mock_stream: MagicMock,
    fixture_cohere_async_response_chunks: AsyncGenerator[
        StreamedChatResponse_TextGeneration, Any
    ],
):
    """Tests `AnthropicPrompt.stream` with logfire."""
    mock_stream.return_value = fixture_cohere_async_response_chunks
    mock_stream.__name__ = "stream"

    my_call = CohereTempCall()
    stream = my_call.stream_async()
    async for chunk in stream:
        assert isinstance(chunk.chunk, StreamedChatResponse_TextGeneration)
    assert my_call.call_params.logfire_async is not None


@with_logfire
class AnthropicTestCall(AnthropicCall):
    prompt_template = ""
    api_key = "test"


@patch(
    "anthropic.resources.messages.Messages.stream",
    new_callable=MagicMock,
)
def test_anthropic_call_stream(
    mock_stream: MagicMock,
    fixture_anthropic_message_chunks: ContextManager[list],
):
    """Tests `AnthropicPrompt.stream` returns the expected response when called."""
    mock_stream.return_value = fixture_anthropic_message_chunks
    mock_stream.__name__ = "stream"

    my_call = AnthropicTestCall()
    stream = my_call.stream()
    for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
    assert my_call.call_params.logfire is not None


@patch(
    "anthropic.resources.messages.AsyncMessages.stream",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_anthropic_call_stream_async(
    mock_stream: MagicMock,
    fixture_anthropic_async_message_chunks: AsyncContextManager[list],
):
    """Tests `AnthropicPrompt.stream` returns the expected response when called."""
    mock_stream.return_value = fixture_anthropic_async_message_chunks
    mock_stream.__name__ = "stream"

    my_call = AnthropicTestCall()
    stream = my_call.stream_async()
    async for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
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


def test_vectorstore_with_logfire() -> None:
    @with_logfire
    class MyStore(ChromaVectorStore):
        embedder = OpenAIEmbedder()
        chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        index_name = "test-0001"

    my_store = MyStore()
    assert my_store.vectorstore_params.logfire is not None


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
