"""Tests for mirascope async openai chat API model classes."""
from unittest.mock import AsyncMock, patch

import pytest

from mirascope.chat.models import AsyncOpenAIChat
from mirascope.chat.types import OpenAIChatCompletion, OpenAIChatCompletionChunk
from mirascope.chat.utils import get_openai_messages_from_prompt

pytestmark = pytest.mark.asyncio


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.parametrize("prompt", ["fixture_foobar_prompt", "fixture_messages_prompt"])
async def test_async_openai_chat(
    mock_create,
    fixture_chat_completion,
    prompt,
    request,
):
    """Tests that `AsyncOpenAIChat` returns the expected response when called."""
    prompt = request.getfixturevalue(prompt)
    mock_create.return_value = fixture_chat_completion

    model = "gpt-3.5-turbo-16k"
    chat = AsyncOpenAIChat(model, api_key="test")
    assert chat.model == model
    completion = await chat.create(prompt, temperature=0.3)
    assert isinstance(completion, OpenAIChatCompletion)

    mock_create.assert_called_once_with(
        model=model,
        messages=get_openai_messages_from_prompt(prompt),
        stream=False,
        temperature=0.3,
    )


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.parametrize(
    "prompt,tools",
    [
        ("fixture_foobar_prompt", ["fixture_my_tool"]),
        ("fixture_foobar_prompt", ["fixture_my_tool", "fixture_empty_tool"]),
    ],
)
async def test_async_openai_chat_tools(
    mock_create, fixture_chat_completion_with_tools, prompt, tools, request
):
    """Tests that `AsyncOpenAIChat` returns the expected response when called with tools."""
    prompt = request.getfixturevalue(prompt)
    tools = [request.getfixturevalue(tool) for tool in tools]
    mock_create.return_value = fixture_chat_completion_with_tools

    chat = AsyncOpenAIChat(api_key="test")
    completion = await chat.create(prompt, tools=tools)
    assert isinstance(completion, OpenAIChatCompletion)

    mock_create.assert_called_once_with(
        model="gpt-3.5-turbo",
        messages=get_openai_messages_from_prompt(prompt),
        stream=False,
        tools=[tool.tool_schema() for tool in tools],
        tool_choice="auto",
    )


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
    side_effect=Exception("base exception"),
)
async def test_async_openai_chat_error(mock_create, fixture_foobar_prompt):
    """Tests that `AsyncOpenAIChat` handles OpenAI errors thrown during __call__."""
    chat = AsyncOpenAIChat("gpt-3.5-turbo", api_key="test")
    with pytest.raises(Exception):
        await chat.create(fixture_foobar_prompt)


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.parametrize("prompt", ["fixture_foobar_prompt", "fixture_messages_prompt"])
async def test_async_openai_chat_stream(
    mock_create,
    fixture_chat_completion_chunk,
    prompt,
    request,
):
    """Tests that `AsyncOpenAIChat` returns the expected response when streaming."""
    prompt = request.getfixturevalue(prompt)
    mock_create.__aiter__.return_value = [fixture_chat_completion_chunk] * 3

    model = "gpt-3.5-turbo-16k"
    chat = AsyncOpenAIChat(model, api_key="test")
    astream = chat.stream(prompt, temperature=0.3)
    async for chunk in astream:
        assert isinstance(chunk, OpenAIChatCompletionChunk)
        assert chunk.chunk == fixture_chat_completion_chunk
        for i, choice in enumerate(chunk.choices):
            assert choice == fixture_chat_completion_chunk.choices[i]

    mock_create.assert_called_once_with(
        model=model,
        messages=get_openai_messages_from_prompt(prompt),
        stream=True,
        temperature=0.3,
    )


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
    side_effect=Exception("base exception"),
)
async def test_async_openai_chat_stream_error(mock_create, fixture_foobar_prompt):
    """Tests that `AsyyncOpenAIChat` handles OpenAI errors thrown during stream."""
    chat = AsyncOpenAIChat("gpt-3.5-turbo", api_key="test")
    with pytest.raises(Exception):
        astream = chat.stream(fixture_foobar_prompt)
        async for chunk in astream:
            pass
