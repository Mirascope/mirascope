from unittest.mock import MagicMock, patch

import pytest

from mirascope import OpenAIChat, OpenAITool, OpenAIToolStreamParser
from mirascope.chat.utils import get_openai_messages_from_prompt


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
@pytest.mark.parametrize(
    "prompt,fixture_tools",
    [
        ("fixture_foobar_prompt", ["fixture_my_tool"]),
        ("fixture_foobar_prompt", ["fixture_my_tool", "fixture_empty_tool"]),
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
        model="gpt-3.5-turbo",
        messages=get_openai_messages_from_prompt(prompt),
        stream=True,
        tools=[tool.tool_schema() for tool in tools],
        tool_choice="auto",
    )
