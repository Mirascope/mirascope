"""Tests for mirascope AsyncOpenAI chat stream tools parser."""
from unittest.mock import AsyncMock, patch

import pytest

from mirascope import AsyncOpenAIChat, AsyncOpenAIToolStreamParser, OpenAITool

pytestmark = pytest.mark.asyncio


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.parametrize(
    "prompt,fixture_tools",
    [
        ("fixture_foobar_prompt_with_my_tool", ["fixture_my_tool"]),
        (
            "fixture_foobar_prompt_with_my_tool_and_empty_tool",
            ["fixture_my_tool", "fixture_empty_tool"],
        ),
    ],
)
@pytest.mark.parametrize(
    "fixture_chat_completion_chunks_with_tools", ["MyTool"], indirect=True
)
async def test_from_stream(
    mock_create: AsyncMock,
    fixture_chat_completion_chunks_with_tools,
    prompt,
    fixture_tools,
    request: pytest.FixtureRequest,
):
    """Tests that `OpenAIToolStreamParser.from_stream` returns the expected tools."""
    prompt = request.getfixturevalue(prompt)
    tools = [request.getfixturevalue(fixture_tool) for fixture_tool in fixture_tools]

    mock_create.return_value.__aiter__.return_value = (
        fixture_chat_completion_chunks_with_tools
    )
    chat = AsyncOpenAIChat(api_key="test")
    stream = chat.stream(prompt, tools=tools)
    parser = AsyncOpenAIToolStreamParser(tools=tools)
    async for tool in parser.from_stream(stream):
        assert isinstance(tool, OpenAITool)

    mock_create.assert_called_once_with(
        model=prompt.call_params().model,
        messages=prompt.messages,
        stream=True,
        tools=[tool.tool_schema() for tool in tools],
        tool_choice="auto",
    )
