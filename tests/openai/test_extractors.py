"""Tests for the `OpenAIExtractor` class."""
from typing import Callable, Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai.types.chat import ChatCompletion
from pydantic import BaseModel, ValidationError

from mirascope.openai.extractors import OpenAIExtractor
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import OpenAICallParams, OpenAICallResponse


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
        template = "test"

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
        template = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    extracted_schema = await TempExtractor().extract_async()
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
        template = "test"

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
        template = "test"

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
    """Tests that `OpenAIChat` raises a `ValueError` when no tools are provided."""
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[BaseModel]):
        template = "test"

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
    """Tests that `OpenAIChat` raises a `ValueError` when no tools are provided."""
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[BaseModel]):
        template = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    with pytest.raises(AttributeError):
        await TempExtractor().extract_async()


@patch("mirascope.openai.calls.OpenAICall.call", new_callable=MagicMock)
@pytest.mark.parametrize("retries", [0, 1, 3, 5])
def test_openai_extractor_extract_with_validation_error(
    mock_call: AsyncMock,
    retries: int,
    fixture_my_openai_tool_schema: Type[BaseModel],
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_with_bad_tools: ChatCompletion,
):
    """Tests that `OpenAIChat` raises a `ValidationError` when extraction fails."""
    tools = [fixture_my_openai_tool]
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_bad_tools,
        tool_types=tools,
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[BaseModel]):
        template = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    with pytest.raises(ValidationError):
        TempExtractor().extract(retries=retries)

    assert mock_call.call_count == retries + 1


@patch("mirascope.openai.calls.OpenAICall.call_async", new_callable=AsyncMock)
@pytest.mark.parametrize("retries", [0, 1, 3, 5])
@pytest.mark.asyncio
async def test_openai_extractor_extract_async_with_validation_error(
    mock_call: AsyncMock,
    retries: int,
    fixture_my_openai_tool_schema: Type[BaseModel],
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_with_bad_tools: ChatCompletion,
):
    """Tests that `OpenAIChat` raises a `ValidationError` when extraction fails."""
    tools = [fixture_my_openai_tool]
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_bad_tools,
        tool_types=tools,
        start_time=0,
        end_time=0,
    )

    class TempExtractor(OpenAIExtractor[BaseModel]):
        template = "test"

        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema

        call_params = OpenAICallParams(model="gpt-4")

    with pytest.raises(ValidationError):
        await TempExtractor().extract_async(retries=retries)

    assert mock_call.call_count == retries + 1


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
        template = "test"

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
        template = "test"

        extract_schema: Type[str] = str

        call_params = OpenAICallParams(model="gpt-4")

    model = await TempExtractor().extract_async()
    assert isinstance(model, str)
    assert model == "value"

    mock_call.assert_called_once()
