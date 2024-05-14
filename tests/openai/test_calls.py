"""Tests for the `OpenAICall` class."""
from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.completion_create_params import ResponseFormat

from mirascope.openai.calls import OpenAICall, _json_mode_content
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import (
    OpenAICallParams,
    OpenAICallResponse,
    OpenAICallResponseChunk,
)


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_call_call(
    mock_create: MagicMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion: ChatCompletion,
) -> None:
    """Tests `OpenAIPrompt.create` returns the expected response when called."""
    mock_create.return_value = fixture_chat_completion
    kwargs = {"temperature": 0.8}
    response = fixture_openai_test_call.call(retries=2, **kwargs)
    assert response.input_tokens is not None
    assert response.output_tokens is not None
    assert response.usage is not None
    assert isinstance(response, OpenAICallResponse)
    mock_create.assert_called_once_with(
        model=fixture_openai_test_call.call_params.model,
        messages=fixture_openai_test_call.messages(),
        stream=False,
        temperature=kwargs["temperature"],
    )


@patch("openai.resources.chat.completions.Completions.create", new_callable=MagicMock)
def test_openai_call_call_with_tools(
    mock_create: MagicMock,
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_with_tools: ChatCompletion,
) -> None:
    """Tests that tools are properly passed to the create call."""
    mock_create.return_value = fixture_chat_completion_with_tools

    class CallWithTools(OpenAICall):
        prompt_template = "test"

        api_key = "test"
        call_params = OpenAICallParams(model="gpt-4", tools=[fixture_my_openai_tool])

    call_with_tools = CallWithTools()
    response = call_with_tools.call()
    mock_create.assert_called_once_with(
        model="gpt-4",
        messages=call_with_tools.messages(),
        tools=[fixture_my_openai_tool.tool_schema()],
        stream=False,
    )
    assert response.tool_types == [fixture_my_openai_tool]


@patch("openai.resources.chat.completions.Completions.create", new_callable=MagicMock)
def test_openai_call_call_with_tools_json_mode(
    mock_create: MagicMock,
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_my_openai_tool_instance: OpenAITool,
    fixture_chat_completion_with_tools_json_mode: ChatCompletion,
) -> None:
    """Tests that tools are properly passed to the create call."""
    mock_create.return_value = fixture_chat_completion_with_tools_json_mode

    class CallWithTools(OpenAICall):
        prompt_template = "test"

        api_key = "test"
        call_params = OpenAICallParams(
            model="gpt-4",
            tools=[fixture_my_openai_tool],
            response_format=ResponseFormat(type="json_object"),
        )

    call_with_tools = CallWithTools()
    response = call_with_tools.call()
    mock_create.assert_called_once_with(
        model="gpt-4",
        messages=call_with_tools.messages()
        + [
            ChatCompletionUserMessageParam(
                role="user",
                content=_json_mode_content(tool_type=fixture_my_openai_tool),
            )
        ],
        response_format=ResponseFormat(type="json_object"),
        stream=False,
    )
    assert response.tool_types == [fixture_my_openai_tool]
    tool = response.tool
    assert tool is not None
    assert tool.model_dump() == fixture_my_openai_tool_instance.model_dump()


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_call_call_with_wrapper(
    mock_create: MagicMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion: ChatCompletion,
) -> None:
    """Tests `OpenAI` is created with a wrapper in `OpenAIPrompt.create`."""
    mock_create.return_value = fixture_chat_completion
    wrapper = MagicMock()
    wrapper.return_value = OpenAI(api_key="test")

    fixture_openai_test_call.call_params.wrapper = wrapper
    fixture_openai_test_call.call()
    wrapper.assert_called_once()


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_call_call_async(
    mock_create: AsyncMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion: ChatCompletion,
) -> None:
    """Tests `OpenAIPrompt.create` returns the expected response when called."""
    mock_create.return_value = fixture_chat_completion
    kwargs = {"temperature": 0.8}
    response = await fixture_openai_test_call.call_async(retries=2, **kwargs)
    assert isinstance(response, OpenAICallResponse)
    mock_create.assert_called_once_with(
        model=fixture_openai_test_call.call_params.model,
        messages=fixture_openai_test_call.messages(),
        stream=False,
        temperature=kwargs["temperature"],
    )


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_call_call_async_with_wrapper(
    mock_create: AsyncMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion: ChatCompletion,
) -> None:
    """Tests `OpenAI` is created with a wrapper in `OpenAIPrompt.create`."""
    mock_create.return_value = fixture_chat_completion
    wrapper = MagicMock()
    wrapper.return_value = AsyncOpenAI(api_key="test")

    fixture_openai_test_call.call_params.wrapper_async = wrapper
    await fixture_openai_test_call.call_async()
    wrapper.assert_called_once()


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_call_stream(
    mock_create: MagicMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
):
    """Tests `OpenAIPrompt.stream` returns expected response."""
    mock_create.return_value = fixture_chat_completion_chunks

    stream = fixture_openai_test_call.stream()
    last_chunk = None
    for i, chunk in enumerate(stream):
        assert isinstance(chunk, OpenAICallResponseChunk)
        assert chunk.chunk == fixture_chat_completion_chunks[i]
        last_chunk = chunk
    assert last_chunk and last_chunk.delta is None
    assert last_chunk and last_chunk.tool_calls is None
    mock_create.assert_called_once_with(
        model=fixture_openai_test_call.call_params.model,
        messages=fixture_openai_test_call.messages(),
        stream=True,
        stream_options={"include_usage": True},
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_call_stream_with_wrapper(
    mock_create: MagicMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
) -> None:
    """Tests `OpenAI` is created with a wrapper in `OpenAIPrompt.create`."""
    mock_create.return_value = fixture_chat_completion_chunks
    wrapper = MagicMock()
    wrapper.return_value = OpenAI(api_key="test")

    fixture_openai_test_call.call_params.wrapper = wrapper
    stream = fixture_openai_test_call.stream()
    for _ in stream:
        pass
    wrapper.assert_called_once()


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_prompt_stream_async(
    mock_create: AsyncMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
):
    """Tests `OpenAIPrompt.stream` returns expected response."""
    mock_create.return_value.__aiter__.return_value = fixture_chat_completion_chunks

    stream = fixture_openai_test_call.stream_async()

    i = 0
    async for chunk in stream:
        assert isinstance(chunk, OpenAICallResponseChunk)
        assert chunk.chunk == fixture_chat_completion_chunks[i]
        i += 1

    mock_create.assert_called_once_with(
        model=fixture_openai_test_call.call_params.model,
        messages=fixture_openai_test_call.messages(),
        stream=True,
        stream_options={"include_usage": True},
    )


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_call_stream_async_with_wrapper(
    mock_create: AsyncMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
) -> None:
    """Tests `OpenAI` is created with a wrapper in `OpenAIPrompt.create`."""
    mock_create.return_value.__aiter__.return_value = fixture_chat_completion_chunks
    wrapper = MagicMock()
    wrapper.return_value = AsyncOpenAI(api_key="test")

    fixture_openai_test_call.call_params.wrapper_async = wrapper
    stream = fixture_openai_test_call.stream_async()
    async for _ in stream:
        pass
    wrapper.assert_called_once()
