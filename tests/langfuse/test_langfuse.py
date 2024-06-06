"""Tests for the Mirascope + Langfuse integration."""

import os
from typing import AsyncContextManager, ContextManager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cohere import StreamedChatResponse_TextGeneration
from cohere.types import NonStreamedChatResponse, StreamedChatResponse
from google.ai.generativelanguage import GenerateContentResponse
from groq.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from mirascope.anthropic.calls import AnthropicCall
from mirascope.anthropic.types import AnthropicCallResponseChunk
from mirascope.cohere.calls import CohereCall
from mirascope.cohere.embedders import CohereEmbedder
from mirascope.cohere.types import CohereCallParams
from mirascope.gemini.calls import GeminiCall
from mirascope.groq.calls import GroqCall
from mirascope.langfuse.langfuse import mirascope_langfuse_generation, with_langfuse
from mirascope.openai import OpenAICall
from mirascope.openai.embedders import OpenAIEmbedder
from mirascope.openai.extractors import OpenAIExtractor
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import OpenAICallResponse
from mirascope.rag.embedders import BaseEmbedder

os.environ["OPENAI_API_KEY"] = "test"


@patch("mirascope.openai.calls.OpenAICall.call", new_callable=MagicMock)
@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
def test_call_with_langfuse(
    mock_langfuse: MagicMock,
    mock_create: MagicMock,
    fixture_chat_completion: ChatCompletion,
) -> None:
    """Tests that `OpenAICall.call` returns the expected response with langfuse.

    Langfuse OpenAI will wrap client_wrapper instead of llm_ops
    """
    mock_create.return_value = fixture_chat_completion
    mock_create.__name__ = "create"

    @with_langfuse
    class MyCall(OpenAICall):
        ...

    class MyNestedCall(MyCall):
        prompt_template = """Test"""

    my_call = MyNestedCall()
    my_call.call()
    assert len(my_call.configuration.client_wrappers) > 0


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
def test_gemini_call_call_with_langfuse(
    mock_langfuse: MagicMock,
    mock_generate_content: MagicMock,
    fixture_generate_content_response: GenerateContentResponse,
) -> None:
    """Tests that `GeminiClass.call` returns the expected response with Langfuse."""
    mock_generate_content.return_value = fixture_generate_content_response
    mock_generate_content.__name__ = "call"

    @with_langfuse
    class MyGeminiCall(GeminiCall):
        ...

    my_call = MyGeminiCall()
    my_call.call()
    assert len(my_call.configuration.llm_ops) > 0


@patch("cohere.Client.chat", new_callable=MagicMock)
@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
def test_cohere_call_call_with_langfuse(
    mock_langfuse: MagicMock,
    mock_chat: MagicMock,
    fixture_non_streamed_response: NonStreamedChatResponse,
) -> None:
    """Tests that `CohereCall.call` returns the expected response with langfuse."""
    mock_chat.return_value = fixture_non_streamed_response

    @with_langfuse
    class CohereTempCall(CohereCall):
        prompt_template = ""
        api_key = "test"
        call_params = CohereCallParams(preamble="test")

    my_call = CohereTempCall()
    my_call.call()
    assert len(my_call.configuration.llm_ops) > 0


@patch("cohere.Client.chat_stream", new_callable=MagicMock)
@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
def test_cohere_call_stream_with_langfuse(
    mock_langfuse: MagicMock,
    mock_chat_stream: MagicMock,
    fixture_cohere_response_chunks: list[StreamedChatResponse],
) -> None:
    """Tests that `CohereCall.stream` returns the expected response with langfuse."""
    mock_chat_stream.return_value = fixture_cohere_response_chunks
    mock_chat_stream.__name__ = "stream"

    @with_langfuse
    class CohereTempCall(CohereCall):
        prompt_template = ""
        api_key = "test"
        call_params = CohereCallParams(preamble="test")

    my_call = CohereTempCall()
    chunks = [chunk for chunk in my_call.stream()]
    for chunk in chunks:
        assert isinstance(chunk.chunk, StreamedChatResponse_TextGeneration)
    assert len(my_call.configuration.llm_ops) > 0


@patch("cohere.AsyncClient.chat", new_callable=AsyncMock)
@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
@pytest.mark.asyncio
async def test_cohere_call_call_async_with_langfuse(
    mock_langfuse: AsyncMock,
    mock_chat: AsyncMock,
    fixture_non_streamed_response: NonStreamedChatResponse,
) -> None:
    """Tests that `CohereCall.call_async` returns the expected response with langfuse."""
    mock_chat.return_value = fixture_non_streamed_response

    @with_langfuse
    class CohereTempCall(CohereCall):
        prompt_template = ""
        api_key = "test"
        call_params = CohereCallParams(preamble="test")

    my_call = CohereTempCall()
    await my_call.call_async()
    assert len(my_call.configuration.llm_ops) > 0


@patch("cohere.AsyncClient.chat_stream", new_callable=MagicMock)
@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
@pytest.mark.asyncio
async def test_cohere_call_stream_async_with_langfuse(
    mock_langfuse: MagicMock,
    mock_chat_stream: MagicMock,
    fixture_cohere_async_response_chunks,
):
    """Tests `CohereCall.stream_async` returns expected response with logfire."""

    @with_langfuse
    class TempCall(CohereCall):
        prompt_template = ""
        api_key = "test"

    mock_chat_stream.return_value = fixture_cohere_async_response_chunks
    mock_chat_stream.__name__ = "stream"
    my_call = TempCall()
    stream = my_call.stream_async()

    async for chunk in stream:
        assert isinstance(chunk.chunk, StreamedChatResponse_TextGeneration)
    assert len(my_call.configuration.llm_ops) > 0


@patch("mirascope.openai.calls.OpenAICall.call", new_callable=MagicMock)
@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
def test_extractor_with_langfuse(
    mock_langfuse: MagicMock,
    mock_call: MagicMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: type[OpenAITool],
    fixture_my_openai_tool_schema: type[BaseModel],
) -> None:
    """Tests that `OpenAIExtractor.extract()` returns expected response with langfuse.
    Langfuse OpenAI will wrap client_wrapper instead of llm_ops
    """
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_tools,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )

    @with_langfuse
    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: type[BaseModel] = fixture_my_openai_tool_schema

    my_extractor = TempExtractor()
    my_extractor.extract()
    assert len(my_extractor.configuration.client_wrappers) > 0


@patch(
    "anthropic.resources.messages.Messages.stream",
    new_callable=MagicMock,
)
@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
def test_anthropic_call_stream_with_langfuse(
    mock_langfuse: MagicMock,
    mock_stream: MagicMock,
    fixture_anthropic_message_chunks: ContextManager[list],
):
    """Tests that `AnthropicCall.stream` returns the expected response with langfuse."""

    mock_stream.return_value = fixture_anthropic_message_chunks
    mock_stream.__name__ = "stream"

    @with_langfuse
    class AnthropicLangfuseCall(AnthropicCall):
        prompt_template = ""
        api_key = "test"

    my_call = AnthropicLangfuseCall()
    stream = my_call.stream()
    for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
    assert len(my_call.configuration.llm_ops) > 0


@patch(
    "anthropic.resources.messages.AsyncMessages.stream",
    new_callable=MagicMock,
)
@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
@pytest.mark.asyncio
async def test_anthropic_call_stream_async(
    mock_langfuse: MagicMock,
    mock_stream: MagicMock,
    fixture_anthropic_async_message_chunks: AsyncContextManager[list],
):
    """Tests `AnthropicPrompt.stream_async` returns the expected response when called."""
    mock_stream.return_value = fixture_anthropic_async_message_chunks
    mock_stream.__name__ = "stream"

    @with_langfuse
    class AnthropicLangfuseCall(AnthropicCall):
        prompt_template = ""
        api_key = "test"

    my_call = AnthropicLangfuseCall()
    stream = my_call.stream_async()
    async for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
    assert len(my_call.configuration.llm_ops) > 0


@patch(
    "groq.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock
)
@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
@pytest.mark.asyncio
async def test_groq_call_stream_async(
    mock_langfuse: MagicMock,
    mock_create: AsyncMock,
    fixture_chat_completion_stream_response: list[ChatCompletionChunk],
):
    """Tests `GroqCall.stream_async` returns expected response with langfuse."""

    @with_langfuse
    class TempCall(GroqCall):
        prompt_template = ""
        api_key = "test"

    mock_create.return_value.__aiter__.return_value = (
        fixture_chat_completion_stream_response
    )
    mock_create.__name__ = "stream"
    my_call = TempCall()
    stream = my_call.stream_async()
    async for chunk in stream:
        assert isinstance(chunk, ChatCompletionChunk)  # pragma: no cover
    assert len(my_call.configuration.llm_ops) > 0


def test_value_error_on_mirascope_langfuse_generation():
    """Tests that `mirascope_langfuse_generation` raises a `ValueError`.
    One of response_type or response_chunk_type is required.
    """
    with pytest.raises(ValueError):

        def foo():
            ...  # pragma: no cover

        mirascope_langfuse_generation()(foo, "test")


class MyEmbedder(BaseEmbedder):
    def embed(self, input: list[str]) -> list[str]:
        return input  # pragma: no cover

    async def embed_async(self, input: list[str]) -> list[str]:
        return input  # pragma: no cover

    def __call__(self, input: str) -> list[float]:
        return [1, 2, 3]  # pragma: no cover


@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
def test_openai_embedder_with_langfuse(mock_langfuse: MagicMock) -> None:
    @with_langfuse
    class MyEmbedder(OpenAIEmbedder):
        ...

    my_embedder = MyEmbedder()
    assert len(my_embedder.configuration.client_wrappers) > 0


@patch(
    "langfuse.decorators.langfuse_decorator.LangfuseDecorator", new_callable=MagicMock
)
def test_cohere_embedder_with_langfuse(mock_langfuse: MagicMock) -> None:
    @with_langfuse
    class MyOtherEmbedder(CohereEmbedder):
        ...

    my_embedder = MyOtherEmbedder()
    assert len(my_embedder.configuration.llm_ops) > 0
