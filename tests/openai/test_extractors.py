"""Tests for the `OpenAIExtractor` class."""

from typing import Callable, Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from pydantic import BaseModel, ValidationError
from tenacity import RetryError

from mirascope.openai.extractors import OpenAIExtractor
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import (
    OpenAICallParams,
    OpenAICallResponse,
    OpenAICallResponseChunk,
)


@patch("mirascope.openai.calls.OpenAICall.call", new_callable=MagicMock)
def test_openai_extractor_extract(
    mock_call: MagicMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_my_openai_tool_schema: Type[BaseModel],
    fixture_my_openai_tool_schema_instance: BaseModel,
) -> None:
    """Tests the `OpenAIExtractor.extract` standard method."""
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_tools,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    extracted_schema = TempExtractor().extract()
    assert (
        extracted_schema.model_json_schema()
        == fixture_my_openai_tool_schema.model_json_schema()
    )
    assert (
        extracted_schema.model_dump()
        == fixture_my_openai_tool_schema_instance.model_dump()
    )


@patch("mirascope.openai.calls.OpenAICall.call", new_callable=MagicMock)
def test_openai_extractor_extract_with_properties(
    mock_call: MagicMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_my_openai_tool_schema: Type[BaseModel],
    fixture_my_openai_tool_schema_instance: BaseModel,
) -> None:
    """Tests the `OpenAIExtractor.extract` standard method."""
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_tools,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "{test_prop}"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

        @property
        def test_prop(self) -> str:
            return "test"

    extracted_schema = TempExtractor().extract()
    assert (
        extracted_schema.model_json_schema()
        == fixture_my_openai_tool_schema.model_json_schema()
    )
    assert (
        extracted_schema.model_dump()
        == fixture_my_openai_tool_schema_instance.model_dump()
    )


@patch("openai.resources.chat.completions.Completions.create", new_callable=MagicMock)
def test_openai_extractor_extract_with_custom_messages(
    mock_call: MagicMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: Type[OpenAITool],
) -> None:
    """Tests that writing custom messages with an OpenAI extractor works."""
    mock_call.return_value = fixture_chat_completion_with_tools

    messages = [{"role": "user", "content": "ensure this is the message"}]

    class TempExtractor(OpenAIExtractor[OpenAITool]):
        prompt_template = "{test_prop}"
        api_key = "test"

        extract_schema: Type[OpenAITool] = fixture_my_openai_tool

        call_params = OpenAICallParams(model="gpt-4")

        def messages(self):
            return messages

    TempExtractor().extract(retries=2)
    mock_call.assert_called_once_with(
        model="gpt-4",
        stream=False,
        messages=messages,
        tools=[fixture_my_openai_tool.tool_schema()],
    )


@patch("mirascope.openai.calls.OpenAICall.call_async", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_openai_extractor_extract_async(
    mock_call: AsyncMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_my_openai_tool_schema: Type[BaseModel],
    fixture_my_openai_tool_schema_instance: BaseModel,
) -> None:
    """Tests the `OpenAIExtractor.extract` standard method."""
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_tools,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    extracted_schema = await TempExtractor().extract_async(retries=2)
    assert (
        extracted_schema.model_json_schema()
        == fixture_my_openai_tool_schema.model_json_schema()
    )
    assert (
        extracted_schema.model_dump()
        == fixture_my_openai_tool_schema_instance.model_dump()
    )


@patch("mirascope.openai.calls.OpenAICall.call", new_callable=MagicMock)
def test_openai_extractor_extract_callable(
    mock_call: MagicMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool_function: Callable,
    fixture_my_openai_tool_instance: OpenAITool,
):
    """Tests that a callable can be extracted using `OpenAIChat`."""
    tool = OpenAITool.from_fn(fixture_my_openai_tool_function)
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_tools,
        tool_types=[tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[OpenAITool]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Callable = fixture_my_openai_tool_function
        call_params = OpenAICallParams(model="gpt-4")

    model = TempExtractor().extract()
    assert isinstance(model, tool)
    assert fixture_my_openai_tool_instance.args == model.args

    mock_call.assert_called_once()


@patch("mirascope.openai.calls.OpenAICall.call_async", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_openai_extractor_extract_async_callable(
    mock_call: AsyncMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool_function: Callable,
    fixture_my_openai_tool_instance: OpenAITool,
):
    """Tests that a callable can be extracted using `OpenAIChat`."""
    tool = OpenAITool.from_fn(fixture_my_openai_tool_function)
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_tools,
        tool_types=[tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[OpenAITool]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Callable = fixture_my_openai_tool_function

        call_params = OpenAICallParams(model="gpt-4")

    model = await TempExtractor().extract_async()
    assert isinstance(model, tool)
    assert fixture_my_openai_tool_instance.args == model.args

    mock_call.assert_called_once()


@patch("mirascope.openai.calls.OpenAICall.call", new_callable=MagicMock)
def test_openai_extractor_extract_with_no_tools(
    mock_call: MagicMock,
    fixture_chat_completion: ChatCompletion,
    fixture_my_openai_tool_schema: Type[BaseModel],
    fixture_my_openai_tool: Type[OpenAITool],
):
    """Tests that `OpenAIChat` raises a `AttributeError` when no tools are provided."""
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    with pytest.raises(AttributeError):
        TempExtractor().extract()


@patch("mirascope.openai.calls.OpenAICall.call_async", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_openai_extractor_extract_async_with_no_tools(
    mock_call: AsyncMock,
    fixture_chat_completion: ChatCompletion,
    fixture_my_openai_tool_schema: Type[BaseModel],
    fixture_my_openai_tool: Type[OpenAITool],
):
    """Tests that `OpenAIChat` raises a `AttributeError` when no tools are provided."""
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    with pytest.raises(AttributeError):
        await TempExtractor().extract_async()


@patch("mirascope.openai.calls.OpenAICall.call", new_callable=MagicMock)
@pytest.mark.parametrize("retries,call_count", [(0, 1), (1, 1), (3, 3), (5, 5)])
def test_openai_extractor_extract_with_validation_error(
    mock_call: MagicMock,
    retries: int,
    call_count: int,
    fixture_my_openai_tool_schema: Type[BaseModel],
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_with_bad_tools: ChatCompletion,
):
    """Tests that `OpenAIChat` raises a `ValidationError` when extraction fails.

    This will raise a RetryError when retries > 0.
    """
    tools = [fixture_my_openai_tool]
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_bad_tools,
        tool_types=tools,
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    if retries > 0:
        with pytest.raises(RetryError):
            TempExtractor().extract(retries=retries)
    else:
        with pytest.raises(ValidationError):
            TempExtractor().extract(retries=retries)

    assert mock_call.call_count == call_count


@patch("mirascope.openai.calls.OpenAICall.call_async", new_callable=AsyncMock)
@pytest.mark.parametrize("retries,call_count", [(0, 1), (1, 1), (3, 3), (5, 5)])
@pytest.mark.asyncio
async def test_openai_extractor_extract_async_with_validation_error(
    mock_call: AsyncMock,
    retries: int,
    call_count: int,
    fixture_my_openai_tool_schema: Type[BaseModel],
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_with_bad_tools: ChatCompletion,
):
    """Tests that `OpenAIChat` raises a `ValidationError` when extraction fails.

    This will raise a RetryError when retries > 0.
    """
    tools = [fixture_my_openai_tool]
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_bad_tools,
        tool_types=tools,
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[fixture_my_openai_tool_schema]):  # type: ignore
        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema
        prompt_template = "test"

        api_key = "test"
        call_params = OpenAICallParams(model="gpt-4")

    if retries > 0:
        with pytest.raises(RetryError):
            await TempExtractor().extract_async(retries=retries)
    else:
        with pytest.raises(ValidationError):
            await TempExtractor().extract_async(retries=retries)
    assert mock_call.call_count == call_count


@patch("mirascope.openai.calls.OpenAICall.call", new_callable=MagicMock)
def test_openai_extractor_extract_base_type(
    mock_call: MagicMock,
    fixture_str_tool: Type[OpenAITool],
    fixture_chat_completion_with_str_tool: ChatCompletion,
):
    """Tests that a base type can be extracted using `OpenAIChat`."""
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_str_tool,
        tool_types=[fixture_str_tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[str]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[str] = str

        call_params = OpenAICallParams(model="gpt-4")

    model = TempExtractor().extract()
    assert isinstance(model, str)
    assert model == "value"

    mock_call.assert_called_once()


@patch("mirascope.openai.calls.OpenAICall.call_async", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_openai_prompt_extract_async_base_type(
    mock_call: AsyncMock,
    fixture_str_tool: Type[OpenAITool],
    fixture_chat_completion_with_str_tool: ChatCompletion,
):
    """Tests that a base type can be extracted using `OpenAIChat`."""
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_str_tool,
        tool_types=[fixture_str_tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[str]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[str] = str

        call_params = OpenAICallParams(model="gpt-4")

    model = await TempExtractor().extract_async()
    assert isinstance(model, str)
    assert model == "value"

    mock_call.assert_called_once()


@patch("mirascope.openai.calls.OpenAICall.stream", new_callable=MagicMock)
def test_openai_extractor_stream(
    mock_stream: MagicMock,
    fixture_chat_completion_chunks_with_tools: list[ChatCompletionChunk],
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_my_openai_tool_schema: Type[BaseModel],
) -> None:
    """Tests the `OpenAIExtractor.stream` method."""
    mock_stream.return_value = [
        OpenAICallResponseChunk(chunk=chunk, tool_types=[fixture_my_openai_tool])
        for chunk in fixture_chat_completion_chunks_with_tools
    ]

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    partial_schemas = list(TempExtractor().stream(retries=2))
    assert len(partial_schemas) == 3
    assert partial_schemas[0].model_dump() == {"param": "param", "optional": None}
    assert partial_schemas[1].model_dump() == {"param": "param", "optional": 0}
    assert partial_schemas[2].model_dump() == {"param": "param", "optional": 0}


@patch("mirascope.openai.calls.OpenAICall.stream_async", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_openai_extractor_stream_async(
    mock_stream: MagicMock,
    fixture_chat_completion_chunks_with_tools: list[ChatCompletionChunk],
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_my_openai_tool_schema: Type[BaseModel],
) -> None:
    """Tests the `OpenAIExtractor.stream_async` method."""
    mock_stream.return_value.__aiter__.return_value = [
        OpenAICallResponseChunk(chunk=chunk, tool_types=[fixture_my_openai_tool])
        for chunk in fixture_chat_completion_chunks_with_tools
    ]

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    partial_schemas = [
        schema async for schema in TempExtractor().stream_async(retries=2)
    ]
    assert len(partial_schemas) == 3
    assert partial_schemas[0].model_dump() == {"param": "param", "optional": None}
    assert partial_schemas[1].model_dump() == {"param": "param", "optional": 0}
    assert partial_schemas[2].model_dump() == {"param": "param", "optional": 0}


@patch("mirascope.openai.calls.OpenAICall.stream", new_callable=MagicMock)
@pytest.mark.parametrize("retries,call_count", [(0, 1), (1, 1), (3, 3), (5, 5)])
def test_openai_extractor_stream_with_validation_error(
    mock_stream: MagicMock,
    retries: int,
    call_count: int,
    fixture_my_openai_tool_schema: Type[BaseModel],
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_chunk_with_bad_tools: ChatCompletionChunk,
):
    """Tests that `OpenAIExtractor` raises a `ValidationError` when extraction fails.

    This will raise a RetryError when retries > 0.
    """
    mock_stream.return_value = [
        OpenAICallResponseChunk(
            chunk=fixture_chat_completion_chunk_with_bad_tools,
            tool_types=[fixture_my_openai_tool],
        )
    ]

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    if retries > 0:
        with pytest.raises(RetryError):
            for _ in TempExtractor().stream(retries=retries):
                pass  # pragma: no cover
    else:
        with pytest.raises(ValidationError):
            for _ in TempExtractor().stream(retries=retries):
                pass  # pragma: no cover

    assert mock_stream.call_count == call_count


@patch("mirascope.openai.calls.OpenAICall.stream_async", new_callable=MagicMock)
@pytest.mark.parametrize("retries,call_count", [(0, 1), (1, 1), (3, 3), (5, 5)])
@pytest.mark.asyncio
async def test_openai_extractor_stream_async_with_validation_error(
    mock_stream: MagicMock,
    retries: int,
    call_count: int,
    fixture_my_openai_tool_schema: Type[BaseModel],
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_chunk_with_bad_tools: ChatCompletionChunk,
):
    """Tests that `OpenAIExtractor` raises a `ValidationError` when extraction fails.

    This will raise a RetryError when retries > 0.
    """
    mock_stream.return_value.__aiter__.return_value = [
        OpenAICallResponseChunk(
            chunk=fixture_chat_completion_chunk_with_bad_tools,
            tool_types=[fixture_my_openai_tool],
        )
    ]

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    if retries > 0:
        with pytest.raises(RetryError):
            async for _ in TempExtractor().stream_async(retries=retries):
                pass  # pragma: no cover
    else:
        with pytest.raises(ValidationError):
            async for _ in TempExtractor().stream_async(retries=retries):
                pass  # pragma: no cover

    assert mock_stream.call_count == call_count


@patch("mirascope.openai.calls.OpenAICall.stream", new_callable=MagicMock)
def test_openai_extractor_stream_no_tool(
    mock_stream: MagicMock,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
    fixture_my_openai_tool_schema: Type[BaseModel],
):
    """Tests `OpenAIExtractor` raises a `AttributeError` when no tools is present."""
    mock_stream.return_value = [
        OpenAICallResponseChunk(chunk=chunk) for chunk in fixture_chat_completion_chunks
    ]

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    with pytest.raises(AttributeError):
        for _ in TempExtractor().stream():
            pass  # pragma: no cover


@patch("mirascope.openai.calls.OpenAICall.stream_async", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_openai_extractor_stream_async_no_tool(
    mock_stream: MagicMock,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
    fixture_my_openai_tool_schema: Type[BaseModel],
):
    """Tests `OpenAIExtractor` raises a `AttributeError` when no tools is present."""
    mock_stream.return_value.__aiter__.return_value = [
        OpenAICallResponseChunk(chunk=chunk) for chunk in fixture_chat_completion_chunks
    ]

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    with pytest.raises(AttributeError):
        async for _ in TempExtractor().stream_async():
            pass  # pragma: no cover


@patch("mirascope.openai.calls.OpenAICall.stream", new_callable=MagicMock)
def test_openai_extractor_stream_only_first_tool(
    mock_stream: MagicMock,
    fixture_chat_completion_chunks_with_tools: list[ChatCompletionChunk],
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_my_openai_tool_schema: Type[BaseModel],
):
    """Tests that `OpenAIExtractor` only extracts the first tool."""
    mock_stream.return_value = [
        OpenAICallResponseChunk(chunk=chunk, tool_types=[fixture_my_openai_tool])
        for chunk in fixture_chat_completion_chunks_with_tools
    ] * 2

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    partial_schemas = list(TempExtractor().stream())
    assert len(partial_schemas) == 3


@patch("mirascope.openai.calls.OpenAICall.stream_async", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_openai_extractor_stream_async_only_first_tool(
    mock_stream: MagicMock,
    fixture_chat_completion_chunks_with_tools: list[ChatCompletionChunk],
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_my_openai_tool_schema: Type[BaseModel],
):
    """Tests that `OpenAIExtractor` only extracts the first tool."""
    mock_stream.return_value.__aiter__.return_value = [
        OpenAICallResponseChunk(chunk=chunk, tool_types=[fixture_my_openai_tool])
        for chunk in fixture_chat_completion_chunks_with_tools
    ] * 2

    class TempExtractor(OpenAIExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    partial_schemas = list([p async for p in TempExtractor().stream_async()])
    assert len(partial_schemas) == 3
