"""Tests for mirascope openai prompt."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import AsyncOpenAI, OpenAI
from pydantic import ValidationError

from mirascope.openai.prompt import OpenAIPrompt
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import (
    OpenAICallParams,
    OpenAIChatCompletion,
    OpenAIChatCompletionChunk,
)


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_prompt_create(
    mock_create, fixture_openai_test_prompt, fixture_chat_completion
):
    """Tests `OpenAIPrompt.create` returns the expected response when called."""
    mock_create.return_value = fixture_chat_completion

    temperature = 0.3
    fixture_openai_test_prompt.call_params.temperature = temperature
    completion = fixture_openai_test_prompt.create()
    assert isinstance(completion, OpenAIChatCompletion)
    assert fixture_openai_test_prompt._start_time is not None
    assert fixture_openai_test_prompt._end_time is not None
    mock_create.assert_called_once_with(
        model=fixture_openai_test_prompt.call_params.model,
        messages=fixture_openai_test_prompt.messages,
        stream=False,
        temperature=temperature,
    )


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_prompt_async_create(
    mock_create, fixture_openai_test_prompt, fixture_chat_completion
):
    """Tests `OpenAIPrompt.async_create` returns the expected response when called."""
    mock_create.return_value = fixture_chat_completion

    completion = await fixture_openai_test_prompt.async_create()
    assert isinstance(completion, OpenAIChatCompletion)
    assert fixture_openai_test_prompt._start_time is not None
    assert fixture_openai_test_prompt._end_time is not None
    print(fixture_openai_test_prompt.call_params.temperature)
    mock_create.assert_called_once_with(
        model=fixture_openai_test_prompt.call_params.model,
        messages=fixture_openai_test_prompt.messages,
        stream=False,
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_prompt_create_with_wrapper(
    mock_create, fixture_openai_test_prompt, fixture_chat_completion
):
    """Tests `OpenAI` is created with a wrapper in `OpenAIPrompt.create`."""
    mock_create.return_value = fixture_chat_completion
    wrapper = MagicMock()
    wrapper.return_value = OpenAI(api_key="test")

    fixture_openai_test_prompt.call_params.wrapper = wrapper
    fixture_openai_test_prompt.create()
    wrapper.assert_called_once()


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_prompt_async_create_with_wrapper(
    mock_create, fixture_openai_test_prompt, fixture_chat_completion
):
    """Tests `AsyncOpenAI` is created with a wrapper in `OpenAIPrompt.async_create`."""
    mock_create.return_value = fixture_chat_completion
    wrapper = MagicMock()
    wrapper.return_value = AsyncOpenAI(api_key="test")

    fixture_openai_test_prompt.call_params.async_wrapper = wrapper
    await fixture_openai_test_prompt.async_create()

    wrapper.assert_called_once()


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_prompt_create_with_tools(
    mock_create,
    fixture_openai_test_prompt,
    fixture_chat_completion_with_tools,
    fixture_my_tool,
):
    """Tests `OpenAIPrompt.create` returns expected response with tools."""

    def tool(param: str):
        """A test function.

        Args:
            param: a string parameter.
        """

    tools = [fixture_my_tool, tool]
    fixture_openai_test_prompt.call_params.tools = tools
    mock_create.return_value = fixture_chat_completion_with_tools

    completion = fixture_openai_test_prompt.create()
    assert isinstance(completion, OpenAIChatCompletion)

    tools[-1] = OpenAITool.from_fn(tool)
    mock_create.assert_called_once_with(
        model=fixture_openai_test_prompt.call_params.model,
        messages=fixture_openai_test_prompt.messages,
        stream=False,
        tools=[tool.tool_schema() for tool in tools],
        tool_choice="auto",
    )


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_prompt_async_create_with_tools(
    mock_create,
    fixture_openai_test_prompt,
    fixture_chat_completion_with_tools,
    fixture_my_tool,
):
    """Tests `OpenAIPrompt.async_create` returns expected response with tools."""
    tools = [fixture_my_tool]
    fixture_openai_test_prompt.call_params.tools = tools
    mock_create.return_value = fixture_chat_completion_with_tools

    completion = await fixture_openai_test_prompt.async_create()
    assert isinstance(completion, OpenAIChatCompletion)

    mock_create.assert_called_once_with(
        model=fixture_openai_test_prompt.call_params.model,
        messages=fixture_openai_test_prompt.messages,
        stream=False,
        tools=[tool.tool_schema() for tool in tools],
        tool_choice="auto",
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
    side_effect=Exception("base exception"),
)
def test_openai_prompt_create_error(mock_create, fixture_openai_test_prompt):
    """Tests that `OpenAIChat` handles OpenAI errors thrown during create."""
    with pytest.raises(Exception):
        fixture_openai_test_prompt.create()


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
    side_effect=Exception("base exception"),
)
@pytest.mark.asyncio
async def test_openai_prompt_async_create_error(
    mock_create, fixture_openai_test_prompt
):
    """Tests that `OpenAIChat` handles OpenAI errors thrown during create."""
    with pytest.raises(Exception):
        await fixture_openai_test_prompt.async_create()


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_prompt_stream(
    mock_create,
    fixture_openai_test_prompt,
    fixture_chat_completion_chunks,
):
    """Tests `OpenAIPrompt.stream` returns expected response."""
    mock_create.return_value = fixture_chat_completion_chunks

    temperature = 0.3
    fixture_openai_test_prompt.call_params.temperature = temperature
    stream = fixture_openai_test_prompt.stream()

    for i, chunk in enumerate(stream):
        assert isinstance(chunk, OpenAIChatCompletionChunk)
        assert chunk.chunk == fixture_chat_completion_chunks[i]

    mock_create.assert_called_once_with(
        model=fixture_openai_test_prompt.call_params.model,
        messages=fixture_openai_test_prompt.messages,
        stream=True,
        temperature=temperature,
    )


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_prompt_async_stream(
    mock_create,
    fixture_openai_test_prompt,
    fixture_chat_completion_chunks,
):
    """Tests `OpenAIPrompt.async_stream` returns expected response."""
    mock_create.return_value.__aiter__.return_value = fixture_chat_completion_chunks

    temperature = 0.3
    fixture_openai_test_prompt.call_params.temperature = temperature
    astream = fixture_openai_test_prompt.async_stream()

    i = 0
    async for chunk in astream:
        assert isinstance(chunk, OpenAIChatCompletionChunk)
        assert chunk.chunk == fixture_chat_completion_chunks[i]
        i += 1

    mock_create.assert_called_once_with(
        model=fixture_openai_test_prompt.call_params.model,
        messages=fixture_openai_test_prompt.messages,
        stream=True,
        temperature=temperature,
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_prompt_stream_with_wrapper(
    mock_create, fixture_openai_test_prompt, fixture_chat_completion_chunk
):
    """Tests `OpenAI` is created with a wrapper in `OpenAIPrompt.create`."""
    mock_create.return_value = [fixture_chat_completion_chunk]
    wrapper = MagicMock()
    wrapper.return_value = OpenAI(api_key="test")

    fixture_openai_test_prompt.call_params.wrapper = wrapper
    for _ in fixture_openai_test_prompt.stream():
        pass
    wrapper.assert_called_once()


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_prompt_async_stream_with_wrapper(
    mock_create, fixture_openai_test_prompt, fixture_chat_completion_chunk
):
    """Tests `OpenAI` is created with a wrapper in `OpenAIPrompt.create`."""
    mock_create.return_value.__aiter__.return_value = [fixture_chat_completion_chunk]
    wrapper = MagicMock()
    wrapper.return_value = AsyncOpenAI(api_key="test")

    fixture_openai_test_prompt.call_params.async_wrapper = wrapper
    async for _ in fixture_openai_test_prompt.async_stream():
        pass
    wrapper.assert_called_once()


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_prompt_stream_with_tools(
    mock_create,
    fixture_openai_test_prompt,
    fixture_my_tool,
    fixture_chat_completion_chunk_with_tools,
):
    """Tests `OpenAIPrompt.stream` returns expected response with tools."""
    tools = [fixture_my_tool]
    fixture_openai_test_prompt.call_params.tools = tools
    chunks = [fixture_chat_completion_chunk_with_tools] * 3
    mock_create.return_value = chunks

    stream = fixture_openai_test_prompt.stream()

    for i, chunk in enumerate(stream):
        assert chunk.tool_calls == chunks[i].choices[0].delta.tool_calls

    mock_create.assert_called_once_with(
        model=fixture_openai_test_prompt.call_params.model,
        messages=fixture_openai_test_prompt.messages,
        stream=True,
        tools=[tool.tool_schema() for tool in tools],
        tool_choice="auto",
    )


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_prompt_async_stream_with_tools(
    mock_create,
    fixture_openai_test_prompt,
    fixture_my_tool,
    fixture_chat_completion_chunk_with_tools,
):
    """Tests `OpenAIPrompt.async_stream` returns expected response with tools."""
    tools = [fixture_my_tool]
    fixture_openai_test_prompt.call_params.tools = tools
    chunks = [fixture_chat_completion_chunk_with_tools] * 3
    mock_create.return_value.__aiter__.return_value = chunks

    astream = fixture_openai_test_prompt.async_stream()

    i = 0
    async for chunk in astream:
        assert chunk.tool_calls == chunks[i].choices[0].delta.tool_calls
        i += 1

    mock_create.assert_called_once_with(
        model=fixture_openai_test_prompt.call_params.model,
        messages=fixture_openai_test_prompt.messages,
        stream=True,
        tools=[tool.tool_schema() for tool in tools],
        tool_choice="auto",
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
    side_effect=Exception("base exception"),
)
def test_openai_prompt_stream_error(mock_create, fixture_openai_test_prompt):
    """Tests that `OpenAIChat` handles OpenAI errors thrown during create."""
    with pytest.raises(Exception):
        stream = fixture_openai_test_prompt.stream()
        stream.__next__()


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
    side_effect=Exception("base exception"),
)
@pytest.mark.asyncio
async def test_openai_prompt_async_stream_error(
    mock_create, fixture_openai_test_prompt
):
    """Tests that `OpenAIChat` handles OpenAI errors thrown during create."""
    with pytest.raises(Exception):
        await fixture_openai_test_prompt.async_stream().__anext__()


@patch("mirascope.openai.prompt.OpenAIPrompt.create", new_callable=MagicMock)
@pytest.mark.parametrize(
    "schema,tool",
    [("fixture_my_schema", "fixture_my_tool"), ("fixture_my_tool", "fixture_my_tool")],
)
def test_openai_prompt_extract(
    mock_create,
    fixture_openai_test_prompt,
    fixture_my_tool_instance,
    fixture_chat_completion_with_tools,
    schema,
    tool,
    request,
):
    """Tests that `MySchema` can be extracted using `OpenAIChat`."""
    schema = request.getfixturevalue(schema)
    tool = request.getfixturevalue(tool)
    tools = [tool]
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_tools, tool_types=tools
    )
    model = fixture_openai_test_prompt.extract(schema)
    assert isinstance(model, schema)
    assert fixture_my_tool_instance.param == model.param
    assert fixture_my_tool_instance.optional == model.optional

    mock_create.assert_called_once()


@patch("mirascope.openai.prompt.OpenAIPrompt.async_create", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "schema,tool",
    [("fixture_my_schema", "fixture_my_tool"), ("fixture_my_tool", "fixture_my_tool")],
)
@pytest.mark.asyncio
async def test_openai_prompt_async_extract(
    mock_create,
    fixture_openai_test_prompt,
    fixture_my_tool_instance,
    fixture_chat_completion_with_tools,
    schema,
    tool,
    request,
):
    """Tests that `MySchema` can be extracted using `OpenAIChat`."""
    schema = request.getfixturevalue(schema)
    tool = request.getfixturevalue(tool)
    tools = [tool]
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_tools, tool_types=tools
    )
    model = await fixture_openai_test_prompt.async_extract(schema)
    assert isinstance(model, schema)
    assert fixture_my_tool_instance.param == model.param
    assert fixture_my_tool_instance.optional == model.optional

    mock_create.assert_called_once()


@patch("mirascope.openai.prompt.OpenAIPrompt.create", new_callable=MagicMock)
def test_openai_prompt_extract_callable(
    mock_create,
    fixture_openai_test_prompt,
    fixture_my_tool_instance,
    fixture_chat_completion_with_tools,
):
    """Tests that a callable can be extracted using `OpenAIChat`."""

    def my_tool(param: str, optional: int = 0):
        """A test function."""

    tool = OpenAITool.from_fn(my_tool)
    tools = [tool]
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_tools, tool_types=tools
    )
    model = fixture_openai_test_prompt.extract(my_tool)
    assert isinstance(model, tool)
    assert fixture_my_tool_instance.args == model.args

    mock_create.assert_called_once()


@patch("mirascope.openai.prompt.OpenAIPrompt.async_create", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_openai_prompt_async_extract_callable(
    mock_create,
    fixture_openai_test_prompt,
    fixture_my_tool_instance,
    fixture_chat_completion_with_tools,
):
    """Tests that a callable can be extracted using `OpenAIChat`."""

    def my_tool(param: str, optional: int = 0):
        """A test function."""

    tool = OpenAITool.from_fn(my_tool)
    tools = [tool]
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_tools, tool_types=tools
    )
    model = await fixture_openai_test_prompt.async_extract(my_tool)
    assert isinstance(model, tool)
    assert fixture_my_tool_instance.args == model.args

    mock_create.assert_called_once()


@patch("mirascope.openai.prompt.OpenAIPrompt.create", new_callable=MagicMock)
def test_openai_prompt_extract_with_no_tools(
    mock_create,
    fixture_openai_test_prompt,
    fixture_chat_completion,
    fixture_my_schema,
    fixture_my_tool,
):
    """Tests that `OpenAIChat` raises a `ValueError` when no tools are provided."""
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion, tool_types=[fixture_my_tool]
    )
    with pytest.raises(AttributeError):
        fixture_openai_test_prompt.extract(fixture_my_schema)


@patch("mirascope.openai.prompt.OpenAIPrompt.async_create", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_openai_prompt_async_extract_with_no_tools(
    mock_create,
    fixture_openai_test_prompt,
    fixture_chat_completion,
    fixture_my_schema,
    fixture_my_tool,
):
    """Tests that `OpenAIChat` raises a `ValueError` when no tools are provided."""
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion, tool_types=[fixture_my_tool]
    )
    with pytest.raises(AttributeError):
        await fixture_openai_test_prompt.async_extract(fixture_my_schema)


@patch("mirascope.openai.prompt.OpenAIPrompt.create", new_callable=MagicMock)
@pytest.mark.parametrize("retries", [0, 1, 3, 5])
def test_openai_prompt_extract_with_validation_error(
    mock_create,
    retries,
    fixture_openai_test_prompt,
    fixture_my_schema,
    fixture_my_tool,
    fixture_chat_completion_with_bad_tools,
):
    """Tests that `OpenAIChat` raises a `ValidationError` when extraction fails."""
    tools = [fixture_my_tool]
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_bad_tools, tool_types=tools
    )
    with pytest.raises(ValidationError):
        fixture_openai_test_prompt.extract(fixture_my_schema, retries=retries)

    assert mock_create.call_count == retries + 1


@patch("mirascope.openai.prompt.OpenAIPrompt.async_create", new_callable=AsyncMock)
@pytest.mark.parametrize("retries", [0, 1, 3, 5])
@pytest.mark.asyncio
async def test_openai_prompt_async_extract_with_validation_error(
    mock_create,
    retries,
    fixture_openai_test_prompt,
    fixture_my_schema,
    fixture_my_tool,
    fixture_chat_completion_with_bad_tools,
):
    """Tests that `OpenAIChat` raises a `ValidationError` when extraction fails."""
    tools = [fixture_my_tool]
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_bad_tools, tool_types=tools
    )
    with pytest.raises(ValidationError):
        await fixture_openai_test_prompt.async_extract(
            fixture_my_schema, retries=retries
        )

    assert mock_create.call_count == retries + 1


class StrTool(OpenAITool):
    """A wrapper tool for the base string type."""

    value: str


@patch("mirascope.openai.prompt.OpenAIPrompt.create", new_callable=MagicMock)
def test_openai_prompt_extract_base_type(
    mock_create,
    fixture_openai_test_prompt,
    fixture_chat_completion_with_str_tool,
):
    """Tests that a base type can be extracted using `OpenAIChat`."""
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_str_tool, tool_types=[StrTool]
    )
    model = fixture_openai_test_prompt.extract(str)
    assert isinstance(model, str)
    assert model == "value"

    mock_create.assert_called_once()


@patch("mirascope.openai.prompt.OpenAIPrompt.async_create", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_openai_prompt_async_extract_base_type(
    mock_create,
    fixture_openai_test_prompt,
    fixture_chat_completion_with_str_tool,
):
    """Tests that a base type can be extracted using `OpenAIChat`."""
    mock_create.return_value = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_str_tool, tool_types=[StrTool]
    )
    model = await fixture_openai_test_prompt.async_extract(str)
    assert isinstance(model, str)
    assert model == "value"

    mock_create.assert_called_once()


@patch(
    "mirascope.openai.prompt.OpenAIPrompt.create",
    new_callable=MagicMock,
    side_effect=Exception("base exception"),
)
def test_openai_prompt_extract_error(
    mock_create, fixture_openai_test_prompt, fixture_my_schema
):
    """Tests that `OpenAIChat` handles OpenAI errors thrown during create."""
    with pytest.raises(Exception):
        fixture_openai_test_prompt.extract(fixture_my_schema)


@patch(
    "mirascope.openai.prompt.OpenAIPrompt.async_create",
    new_callable=AsyncMock,
    side_effect=Exception("base exception"),
)
@pytest.mark.asyncio
async def test_openai_prompt_async_extract_error(
    mock_create, fixture_openai_test_prompt, fixture_my_schema
):
    """Tests that `OpenAIChat` handles OpenAI errors thrown during create."""
    with pytest.raises(Exception):
        await fixture_openai_test_prompt.async_extract(fixture_my_schema)


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_prompt_extract_then_create(
    mock_create: MagicMock,
    fixture_chat_completion_with_tools,
    fixture_my_tool,
    fixture_my_schema,
):
    """Tests that calling `create` has no tools after calling `extract`."""
    mock_create.return_value = fixture_chat_completion_with_tools

    class ExtractPrompt(OpenAIPrompt):
        """A prompt for running `extract`."""

        call_params = OpenAICallParams(tools=[fixture_my_tool])

    class CreatePrompt(OpenAIPrompt):
        """A prompt for running `create`."""

    ExtractPrompt().extract(fixture_my_schema)
    assert "tools" in mock_create.call_args.kwargs

    CreatePrompt().create()
    assert "tools" not in mock_create.call_args.kwargs


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_prompt_async_extract_then_async_create(
    mock_create: MagicMock,
    fixture_chat_completion_with_tools,
    fixture_my_tool,
    fixture_my_schema,
):
    """Tests that calling `create` has no tools after calling `extract`."""
    mock_create.return_value = fixture_chat_completion_with_tools

    class ExtractPrompt(OpenAIPrompt):
        """A prompt for running `extract`."""

        call_params = OpenAICallParams(tools=[fixture_my_tool])

    class CreatePrompt(OpenAIPrompt):
        """A prompt for running `create`."""

    await ExtractPrompt().async_extract(fixture_my_schema)
    assert "tools" in mock_create.call_args.kwargs

    await CreatePrompt().async_create()
    assert "tools" not in mock_create.call_args.kwargs
