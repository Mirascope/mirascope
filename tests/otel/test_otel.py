"""Tests for the Mirascope + OTel integration."""
import os
from typing import AsyncContextManager, ContextManager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cohere import StreamedChatResponse_TextGeneration
from cohere.types import NonStreamedChatResponse
from google.ai.generativelanguage import GenerateContentResponse
from groq.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk as OpenAIChatCompletionChunk,
)
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from pydantic import BaseModel

from mirascope.anthropic.calls import AnthropicCall
from mirascope.anthropic.types import AnthropicCallParams, AnthropicCallResponseChunk
from mirascope.base.types import BaseConfig
from mirascope.cohere.calls import CohereCall
from mirascope.cohere.types import CohereCallParams
from mirascope.gemini.calls import GeminiCall
from mirascope.groq.calls import GroqCall
from mirascope.groq.types import GroqCallParams
from mirascope.openai import OpenAICall, OpenAIExtractor
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import OpenAICallParams
from mirascope.otel import with_otel
from mirascope.otel.otel import configure, mirascope_otel
from tests.otel.conftest import CapOtel

os.environ["OPENAI_API_KEY"] = "test"

openai_model = "gpt-3.5-turbo"


def test_configure():
    """Tests that `configure` works."""
    configure(processors=[SimpleSpanProcessor(ConsoleSpanExporter())])


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_call_with_otel(
    mock_create: MagicMock,
    fixture_chat_completion: ChatCompletion,
    fixture_capotel: CapOtel,
) -> None:
    mock_create.return_value = fixture_chat_completion
    mock_create.__name__ = "call"

    class MyCall(OpenAICall):
        ...

    @with_otel
    class MyNestedCall(MyCall):
        prompt_template = "test"

        call_params = OpenAICallParams(
            model="gpt-3.5-turbo", temperature=0.1, top_p=0.9
        )
        configuration = BaseConfig(llm_ops=[], client_wrappers=[])

    MyNestedCall().call()
    span_list = fixture_capotel.exporter.get_finished_spans()
    assert span_list[0].name == "openai.call with gpt-3.5-turbo"
    assert span_list[1].name == "MyNestedCall.call"


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_stream_with_otel(
    mock_create: MagicMock,
    fixture_capotel: CapOtel,
    fixture_chat_completion_chunks: list[OpenAIChatCompletionChunk],
) -> None:
    fixture_capotel.exporter.clear()
    mock_create.return_value = fixture_chat_completion_chunks
    mock_create.__name__ = "call"

    class MyCall(OpenAICall):
        ...

    @with_otel
    class MyNestedCall(MyCall):
        prompt_template = "test"

        call_params = OpenAICallParams(model="gpt-3.5-turbo")
        configuration = BaseConfig(llm_ops=[], client_wrappers=[])

    response = MyNestedCall().stream()
    for chunk in response:
        ...
    span_list = fixture_capotel.exporter.get_finished_spans()
    assert span_list[0].name == "openai.call with gpt-3.5-turbo"
    assert span_list[1].name == "MyNestedCall.stream"


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_gemini_call_call_with_otel(
    mock_generate_content: MagicMock,
    fixture_generate_content_response: GenerateContentResponse,
    fixture_capotel: CapOtel,
) -> None:
    """Tests that `GeminiClass.call` returns the expected response."""
    fixture_capotel.exporter.clear()
    mock_generate_content.return_value = fixture_generate_content_response
    mock_generate_content.__name__ = "call"

    @with_otel
    class MyGeminiCall(GeminiCall):
        ...

    my_call = MyGeminiCall()
    my_call.call()
    span_list = fixture_capotel.exporter.get_finished_spans()
    assert span_list[0].name == "gemini.call with gemini-1.0-pro"
    assert span_list[1].name == "MyGeminiCall.call"


@patch("cohere.AsyncClient.chat", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_cohere_call_call_async_with_otel(
    mock_chat: AsyncMock,
    fixture_non_streamed_response: NonStreamedChatResponse,
    fixture_capotel: CapOtel,
) -> None:
    """Tests that `CohereCall.call_async` returns the expected response with otel."""
    fixture_capotel.exporter.clear()
    mock_chat.return_value = fixture_non_streamed_response

    @with_otel
    class CohereTempCall(CohereCall):
        prompt_template = ""
        api_key = "test"
        call_params = CohereCallParams(preamble="test")

    my_call = CohereTempCall()

    await my_call.call_async()
    span_list = fixture_capotel.exporter.get_finished_spans()
    assert span_list[0].name == "cohere.wrapped with command-r-plus"
    assert span_list[1].name == "CohereTempCall.call_async"


@patch("cohere.AsyncClient.chat_stream", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_cohere_call_stream_async_with_otel(
    mock_chat_stream: MagicMock,
    fixture_cohere_async_response_chunks,
    fixture_capotel: CapOtel,
):
    """Tests `CohereCall.stream_async` returns expected response with otel."""
    fixture_capotel.exporter.clear()

    @with_otel
    class TempCall(CohereCall):
        prompt_template = ""
        api_key = "test"

    mock_chat_stream.return_value = fixture_cohere_async_response_chunks
    mock_chat_stream.__name__ = "wrapped"
    my_call = TempCall()
    stream = my_call.stream_async()

    async for chunk in stream:
        assert isinstance(chunk.chunk, StreamedChatResponse_TextGeneration)
    span_list = fixture_capotel.exporter.get_finished_spans()
    assert span_list[0].name == "cohere.wrapped with command-r-plus"
    assert span_list[1].name == "TempCall.stream_async"


@patch(
    "anthropic.resources.messages.Messages.stream",
    new_callable=MagicMock,
)
def test_anthropic_call_stream(
    mock_stream: MagicMock,
    fixture_anthropic_message_chunks: ContextManager[list],
    fixture_capotel: CapOtel,
):
    """Tests `AnthropicPrompt.stream` returns the expected response when called."""
    fixture_capotel.exporter.clear()
    mock_stream.return_value = fixture_anthropic_message_chunks
    mock_stream.__name__ = "stream"

    @with_otel
    class AnthropicOtelCall(AnthropicCall):
        prompt_template = ""
        api_key = "test"
        call_params = AnthropicCallParams()

    my_call = AnthropicOtelCall()
    stream = my_call.stream()
    for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
    span_list = fixture_capotel.exporter.get_finished_spans()
    assert span_list[0].name == "anthropic.stream with claude-3-haiku-20240307"
    assert span_list[1].name == "AnthropicOtelCall.stream"


@patch(
    "anthropic.resources.messages.AsyncMessages.stream",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_anthropic_call_stream_async(
    mock_stream: MagicMock,
    fixture_anthropic_async_message_chunks: AsyncContextManager[list],
    fixture_capotel: CapOtel,
):
    """Tests `AnthropicPrompt.stream_async` returns the expected response when called."""
    fixture_capotel.exporter.clear()
    mock_stream.return_value = fixture_anthropic_async_message_chunks
    mock_stream.__name__ = "stream"

    @with_otel
    class AnthropicOtelCall(AnthropicCall):
        prompt_template = ""
        api_key = "test"
        call_params = AnthropicCallParams()

    my_call = AnthropicOtelCall()
    stream = my_call.stream_async()
    async for chunk in stream:
        assert isinstance(chunk, AnthropicCallResponseChunk)
    span_list = fixture_capotel.exporter.get_finished_spans()
    assert span_list[0].name == "anthropic.stream with claude-3-haiku-20240307"
    assert span_list[1].name == "AnthropicOtelCall.stream_async"


@patch(
    "groq.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_groq_call_stream_async_with_otel(
    mock_create: AsyncMock,
    fixture_chat_completion_stream_response: list[ChatCompletionChunk],
    fixture_capotel: CapOtel,
):
    """Tests `GroqCall.stream_async` returns expected response with otel."""
    fixture_capotel.exporter.clear()

    @with_otel
    class TempCall(GroqCall):
        prompt_template = ""
        api_key = "test"
        call_params = GroqCallParams(model="llama3-8b-8192")

    mock_create.return_value.__aiter__.return_value = (
        fixture_chat_completion_stream_response
    )
    mock_create.__name__ = "stream"
    my_call = TempCall()
    stream = my_call.stream_async()
    async for chunk in stream:
        pass  # pragma: no cover

    span_list = fixture_capotel.exporter.get_finished_spans()
    assert span_list[0].name == "groq.stream with llama3-8b-8192"
    assert span_list[1].name == "TempCall.stream_async"


@patch("openai.resources.chat.completions.Completions.create", new_callable=MagicMock)
def test_extractor_with_otel(
    mock_call: MagicMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: type[OpenAITool],
    fixture_my_openai_tool_schema: type[BaseModel],
    fixture_capotel: CapOtel,
) -> None:
    fixture_capotel.exporter.clear()
    mock_call.return_value = fixture_chat_completion_with_tools
    mock_call.__name__ = "call"

    @with_otel
    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"
        call_params = OpenAICallParams(
            model=openai_model, tools=[fixture_my_openai_tool]
        )
        extract_schema: type[BaseModel] = fixture_my_openai_tool_schema
        configuration = BaseConfig(llm_ops=[], client_wrappers=[])

    my_extractor = TempExtractor()
    my_extractor.extract()
    span_list = fixture_capotel.exporter.get_finished_spans()
    assert span_list[0].name == "openai.call with gpt-3.5-turbo"
    assert span_list[1].name == "TempExtractor.extract"


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_async_extractor_with_otel(
    mock_call: MagicMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: type[OpenAITool],
    fixture_my_openai_tool_schema: type[BaseModel],
    fixture_capotel: CapOtel,
) -> None:
    fixture_capotel.exporter.clear()
    mock_call.return_value = fixture_chat_completion_with_tools
    mock_call.__name__ = "call"

    @with_otel
    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"
        call_params = OpenAICallParams(
            model=openai_model, tools=[fixture_my_openai_tool]
        )
        extract_schema: type[BaseModel] = fixture_my_openai_tool_schema
        configuration = BaseConfig(llm_ops=[], client_wrappers=[])

    my_extractor = TempExtractor()
    await my_extractor.extract_async()
    span_list = fixture_capotel.exporter.get_finished_spans()
    assert span_list[0].name == "openai.call with gpt-3.5-turbo"
    assert span_list[1].name == "TempExtractor.extract_async"


def test_value_error_on_mirascope_otel():
    """Tests that `mirascope_otel` raises a `ValueError`.
    One of response_type or response_chunk_type is required.
    """
    with pytest.raises(ValueError):

        def foo():
            ...  # pragma: no cover

        mirascope_otel(BaseModel)(foo, "test")


@patch("cohere.Client.chat", new_callable=MagicMock)
def test_stdout_exporter(
    mock_chat: MagicMock,
    fixture_non_streamed_response: NonStreamedChatResponse,
):
    """Tests that `mirascope_otel` with stdout exporter works."""
    mock_chat.return_value = fixture_non_streamed_response
    mock_chat.__name__ = "call"

    @with_otel
    class CohereTempCall(CohereCall):
        prompt_template = ""
        api_key = "test"
        call_params = CohereCallParams(preamble="test")

    CohereTempCall().call()
