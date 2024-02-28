"""Tests for mirascope OpenAI chat stream tools parser."""
from unittest.mock import MagicMock, patch

import pytest

from mirascope import OpenAIChat, OpenAITool, OpenAIToolStreamParser


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
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
def test_from_stream(
    mock_create: MagicMock,
    fixture_chat_completion_chunks_with_tools,
    prompt,
    fixture_tools,
    request: pytest.FixtureRequest,
):
    """Tests that `OpenAIToolStreamParser.from_stream` returns the expected tools."""
    prompt = request.getfixturevalue(prompt)

    tools = [request.getfixturevalue(fixture_tool) for fixture_tool in fixture_tools]
    mock_create.return_value = fixture_chat_completion_chunks_with_tools
    chat = OpenAIChat(api_key="test")
    stream = chat.stream(prompt, tools=tools)
    parser = OpenAIToolStreamParser(tools=tools)
    for tool in parser.from_stream(stream):
        assert isinstance(tool, OpenAITool)

    mock_create.assert_called_once_with(
        model=prompt.call_params.model,
        messages=prompt.messages,
        stream=True,
        tools=[tool.tool_schema() for tool in tools],
        tool_choice="auto",
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
@pytest.mark.parametrize(
    "fixture_chat_completion_chunks_with_tools", ["MyTool"], indirect=True
)
def test_from_stream_no_tool(
    mock_create: MagicMock,
    fixture_chat_completion_chunks_with_tools,
    fixture_foobar_prompt,
    request: pytest.FixtureRequest,
):
    """Tests `OpenAIToolStreamParser.from_stream` with no tools."""

    mock_create.return_value = fixture_chat_completion_chunks_with_tools
    chat = OpenAIChat(api_key="test")
    stream = chat.stream(fixture_foobar_prompt)
    parser = OpenAIToolStreamParser(tools=[])
    assert sum(1 for _ in parser.from_stream(stream)) == 0

    print(fixture_foobar_prompt.call_params)

    mock_create.assert_called_once_with(
        model=fixture_foobar_prompt.call_params.model,
        messages=fixture_foobar_prompt.messages,
        stream=True,
    )
