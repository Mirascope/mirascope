"""Tests for mirascope openai chat API model classes."""
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, Field, ValidationError

from mirascope.chat.models import OpenAIChat
from mirascope.chat.tools import OpenAITool
from mirascope.chat.types import OpenAIChatCompletion, OpenAIChatCompletionChunk
from mirascope.chat.utils import get_openai_messages_from_prompt
from mirascope.prompts import Prompt


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
@pytest.mark.parametrize(
    "prompt",
    [
        "fixture_foobar_prompt",
        "fixture_messages_prompt",
        "fixture_string_prompt",
    ],
)
def test_openai_chat(
    mock_create,
    fixture_chat_completion,
    prompt,
    request,
):
    """Tests that `OpenAIChat` returns the expected response when called."""
    prompt = request.getfixturevalue(prompt)
    mock_create.return_value = fixture_chat_completion

    model = "gpt-3.5-turbo-16k"
    chat = OpenAIChat(model, api_key="test")
    assert chat.model == model

    completion = chat.create(prompt, temperature=0.3)
    assert isinstance(completion, OpenAIChatCompletion)

    mock_create.assert_called_once_with(
        model=model,
        messages=get_openai_messages_from_prompt(prompt),
        stream=False,
        temperature=0.3,
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_chat_messages_kwarg(mock_create, fixture_chat_completion):
    """Tests that `OpenAIChat` works with a messages prompt."""
    mock_create.return_value = fixture_chat_completion

    model = "gpt-3.5-turbo-16k"
    chat = OpenAIChat(model, api_key="test")
    assert chat.model == model

    messages = [{"role": "user", "content": "content"}]
    completion = chat.create(messages=messages)
    assert isinstance(completion, OpenAIChatCompletion)

    mock_create.assert_called_once_with(
        model=model,
        messages=messages,
        stream=False,
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
@pytest.mark.parametrize(
    "prompt,tools",
    [
        ("fixture_foobar_prompt", ["fixture_my_tool"]),
        ("fixture_foobar_prompt", ["fixture_my_tool", "fixture_empty_tool"]),
    ],
)
def test_openai_chat_tools(
    mock_create, fixture_chat_completion_with_tools, prompt, tools, request
):
    """Tests that `OpenAIChat` returns the expected response when called with tools."""
    prompt = request.getfixturevalue(prompt)
    tools = [request.getfixturevalue(tool) for tool in tools]
    mock_create.return_value = fixture_chat_completion_with_tools

    chat = OpenAIChat(api_key="test")
    completion = chat.create(prompt, tools=tools)
    assert isinstance(completion, OpenAIChatCompletion)

    mock_create.assert_called_once_with(
        model="gpt-3.5-turbo",
        messages=get_openai_messages_from_prompt(prompt),
        stream=False,
        tools=[tool.tool_schema() for tool in tools],
        tool_choice="auto",
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
    side_effect=Exception("base exception"),
)
def test_openai_chat_error(mock_create, fixture_foobar_prompt):
    """Tests that `OpenAIChat` handles OpenAI errors thrown during create."""
    chat = OpenAIChat("gpt-3.5-turbo", api_key="test")
    with pytest.raises(Exception):
        chat.create(fixture_foobar_prompt)


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
@pytest.mark.parametrize(
    "prompt",
    [
        "fixture_foobar_prompt",
        "fixture_messages_prompt",
        "fixture_string_prompt",
    ],
)
def test_openai_chat_stream(
    mock_create,
    fixture_chat_completion_chunk,
    prompt,
    request,
):
    """Tests that `OpenAIChat` returns the expected response when streaming."""
    prompt = request.getfixturevalue(prompt)
    mock_create.return_value = [fixture_chat_completion_chunk] * 3

    model = "gpt-3.5-turbo-16k"
    chat = OpenAIChat(model, api_key="test")
    stream = chat.stream(prompt, temperature=0.3)

    for chunk in stream:
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
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_chat_stream_messages_kwarg(mock_create, fixture_chat_completion_chunk):
    """Tests that `OpenAIChat.stream` works with a messages kwarg."""
    mock_create.return_value = [fixture_chat_completion_chunk] * 3

    model = "gpt-3.5-turbo-16k"
    chat = OpenAIChat(model, api_key="test")
    messages = [{"role": "user", "content": "content"}]
    stream = chat.stream(messages=messages)

    for chunk in stream:
        pass  # we need to call the generator to check the mock create calls

    mock_create.assert_called_once_with(
        model=model,
        messages=messages,
        stream=True,
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
@pytest.mark.parametrize(
    "prompt,tools",
    [
        ("fixture_foobar_prompt", ["fixture_my_tool"]),
        ("fixture_foobar_prompt", ["fixture_my_tool", "fixture_empty_tool"]),
    ],
)
def test_openai_chat_stream_tools(
    mock_create, fixture_chat_completion_chunk_with_tools, prompt, tools, request
):
    """Tests that `OpenAIChat` returns the expected response when called with tools."""
    prompt = request.getfixturevalue(prompt)
    tools = [request.getfixturevalue(tool) for tool in tools]
    chunks = [fixture_chat_completion_chunk_with_tools] * 3
    mock_create.return_value = chunks

    chat = OpenAIChat(api_key="test")
    stream = chat.stream(prompt, tools=tools)

    for i, chunk in enumerate(stream):
        assert chunk.tool_calls == chunks[i].choices[0].delta.tool_calls

    mock_create.assert_called_once_with(
        model="gpt-3.5-turbo",
        messages=get_openai_messages_from_prompt(prompt),
        stream=True,
        tools=[tool.tool_schema() for tool in tools],
        tool_choice="auto",
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
    side_effect=Exception("base exception"),
)
def test_openai_chat_stream_error(mock_create, fixture_foobar_prompt):
    """Tests that `OpenAIChat` handles OpenAI errors thrown during stream."""
    chat = OpenAIChat("gpt-3.5-turbo", api_key="test")
    with pytest.raises(Exception):
        stream = chat.stream(fixture_foobar_prompt)
        for chunk in stream:
            pass


class MySchema(BaseModel):
    """A test schema."""

    param: str = Field(..., description="A test parameter.")
    optional: int = 0


class MySchemaTool(OpenAITool):
    """A test schema."""

    param: str = Field(..., description="A test parameter.")
    optional: int = 0


@patch("mirascope.chat.models.OpenAIChat.create", new_callable=MagicMock)
@pytest.mark.parametrize("prompt", [Prompt(), "This is a test prompt."])
@pytest.mark.parametrize("retries", [1, 3, 5])
def test_openai_chat_extract(
    mock_create,
    prompt,
    retries,
    fixture_my_tool,
    fixture_my_tool_instance,
    fixture_chat_completion_with_tools,
):
    """Tests that `OpenAIChat` can be extracted from a `Chat`."""
    tools = [fixture_my_tool]
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_tools, tool_types=tools
    )
    chat = OpenAIChat("gpt-3.5-turbo", api_key="test")
    prompt = Prompt()
    model = chat.extract(MySchema, prompt, retries=retries)

    mock_create.assert_called_once()

    prompt_arg = mock_create.call_args.args[0]
    assert prompt_arg.model_dump() == prompt.model_dump()

    tools_arg, tool_choice_arg = list(mock_create.call_args.kwargs.values())
    assert len(tools_arg) == 1
    assert tools_arg[0].model_json_schema() == MySchemaTool.model_json_schema()
    assert tool_choice_arg == {"type": "function", "function": {"name": "MySchemaTool"}}
    assert isinstance(model, MySchema)
    assert model.model_dump() == fixture_my_tool_instance.model_dump()


@patch("mirascope.chat.models.OpenAIChat.create", new_callable=MagicMock)
def test_openai_chat_extract_messages_prompt(
    mock_create, fixture_my_tool, fixture_chat_completion_with_tools
):
    """Tests that `OpenAIChat.extract` works with a messages prompt."""
    tools = [fixture_my_tool]
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_tools, tool_types=tools
    )
    chat = OpenAIChat("gpt-3.5-turbo", api_key="test")
    messages = [{"role": "user", "content": "content"}]
    model = chat.extract(MySchema, messages=messages)

    mock_create.assert_called_once()
    assert isinstance(model, MySchema)


@patch("mirascope.chat.models.OpenAIChat.create", new_callable=MagicMock)
@pytest.mark.parametrize("retries", [0, 1, 3, 5])
def test_openai_chat_extract_with_validation_error(
    mock_create, retries, fixture_my_tool, fixture_chat_completion_with_bad_tools
):
    """Tests that `OpenAIChat` raises a `ValidationError` when extraction fails."""
    tools = [fixture_my_tool]
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_bad_tools, tool_types=tools
    )
    chat = OpenAIChat("gpt-3.5-turbo", api_key="test")
    prompt = Prompt()
    with pytest.raises(ValidationError):
        chat.extract(MySchema, prompt, retries=retries)

    assert mock_create.call_count == retries + 1
