"""Tests for the Call and AsyncContextCall classes."""

from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import BaseModel

from mirascope import llm


class Format(BaseModel):
    """Test format for structured responses."""

    ...


@pytest.fixture
def context() -> llm.Context[int]:
    """Create a mock LLM for testing."""
    return llm.Context(deps=42)


@pytest.fixture
def mock_llm() -> Mock:
    """Create a mock LLM for testing."""
    return Mock(spec=llm.Model)


@pytest.fixture
def toolkit() -> llm.ContextToolkit[int]:
    """Create a mock toolkit for testing."""

    @llm.tool
    def tool() -> int:
        return 42

    toolkit = llm.ContextToolkit[int](tools=[tool])
    return toolkit


@pytest.fixture
def async_toolkit() -> llm.AsyncContextToolkit[int]:
    """Create a mock async toolkit for testing."""

    @llm.tool
    async def async_tool() -> int:
        return 42

    toolkit = llm.AsyncContextToolkit[int](tools=[async_tool])
    return toolkit


@pytest.fixture
def mock_prompt() -> llm.prompts.ContextPrompt:
    """Create a mock prompt function."""

    def prompt(ctx: llm.Context[int], name: str, *, title: str = "dr") -> str:
        return f"hi {title} {name} ({ctx.deps})"

    return prompt


@pytest.fixture
def mock_async_prompt() -> llm.prompts.AsyncContextPrompt:
    """Create a mock async prompt function."""

    async def prompt(ctx: llm.Context[int], name: str, *, title: str = "dr") -> str:
        return f"hi {title} {name} ({ctx.deps})"

    return prompt


@pytest.fixture
def mock_response() -> Mock:
    """Create a mock response for testing."""
    mock_response = Mock(spec=llm.Response)
    mock_response.messages = [
        llm.messages.user("original message"),
        llm.messages.assistant("response"),
    ]
    return mock_response


@pytest.fixture
def mock_stream_response() -> Mock:
    """Create a mock stream response for testing."""
    mock_response = Mock(spec=llm.StreamResponse)
    mock_response.messages = [
        llm.messages.user("original message"),
        llm.messages.assistant("stream response"),
    ]
    return mock_response


@pytest.fixture
def mock_async_stream_response() -> Mock:
    """Create a mock async stream response for testing."""
    mock_response = Mock(spec=llm.AsyncStreamResponse)
    mock_response.messages = [
        llm.messages.user("original message"),
        llm.messages.assistant("async stream response"),
    ]
    return mock_response


@pytest.fixture
def call_instance(
    mock_llm: Mock,
    toolkit: llm.ContextToolkit[int],
    mock_prompt: llm.prompts.Prompt,
) -> llm.calls.ContextCall:
    """Create a ContextCall instance for testing."""
    return llm.calls.ContextCall(
        default_model=mock_llm, toolkit=toolkit, format=None, fn=mock_prompt
    )


@pytest.fixture
def call_instance_with_format(
    mock_llm: Mock,
    toolkit: llm.ContextToolkit[int],
    mock_prompt: llm.prompts.Prompt,
) -> llm.calls.ContextCall[..., int, Format]:
    """Create a ContextCall instance with format for testing."""
    return llm.calls.ContextCall(
        default_model=mock_llm, toolkit=toolkit, format=Format, fn=mock_prompt
    )


@pytest.fixture
def async_call_instance(
    mock_llm: Mock,
    async_toolkit: llm.AsyncContextToolkit[int],
    mock_async_prompt: llm.prompts.AsyncPrompt,
) -> llm.calls.AsyncContextCall:
    """Create an AsyncContextCall instance for testing."""
    return llm.calls.AsyncContextCall(
        default_model=mock_llm, toolkit=async_toolkit, format=None, fn=mock_async_prompt
    )


@pytest.fixture
def async_call_instance_with_format(
    mock_llm: Mock,
    async_toolkit: llm.AsyncContextToolkit[int],
    mock_async_prompt: llm.prompts.AsyncPrompt,
) -> llm.calls.AsyncContextCall[..., int, Format]:
    """Create an AsyncContextCall instance with format for testing."""
    return llm.calls.AsyncContextCall(
        default_model=mock_llm,
        toolkit=async_toolkit,
        format=Format,
        fn=mock_async_prompt,
    )


def test_sync_dunder_call(
    call_instance: llm.calls.ContextCall,
    mock_llm: Mock,
    mock_response: Mock,
    toolkit: llm.ContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that ContextCall.__call__ passes parameters correctly to model.call."""
    mock_llm.context_call.return_value = mock_response

    result = call_instance(context, "sazed", title="keeper")

    mock_llm.context_call.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=toolkit.tools,
        format=None,
        ctx=context,
    )
    assert result is mock_response


def test_sync_dunder_call_with_format(
    call_instance_with_format: llm.calls.ContextCall,
    mock_llm: Mock,
    mock_response: Mock,
    toolkit: llm.ContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that ContextCall.__call__ with format passes parameters correctly to model.call."""
    mock_llm.context_call.return_value = mock_response

    result = call_instance_with_format(context, "sazed", title="keeper")

    mock_llm.context_call.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=toolkit.tools,
        format=Format,
        ctx=context,
    )
    assert result is mock_response


def test_sync_call_method(
    call_instance: llm.calls.ContextCall,
    mock_llm: Mock,
    mock_response: Mock,
    toolkit: llm.ContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that ContextCall.call passes parameters correctly to model.call."""
    mock_llm.context_call.return_value = mock_response

    result = call_instance.call(context, "sazed", title="keeper")

    mock_llm.context_call.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=toolkit.tools,
        format=None,
        ctx=context,
    )
    assert result is mock_response


def test_sync_call_method_with_format(
    call_instance_with_format: llm.calls.ContextCall,
    mock_llm: Mock,
    mock_response: Mock,
    toolkit: llm.ContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that ContextCall.call with format passes parameters correctly to model.call."""
    mock_llm.context_call.return_value = mock_response

    result = call_instance_with_format.call(context, "sazed", title="keeper")

    mock_llm.context_call.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=toolkit.tools,
        format=Format,
        ctx=context,
    )
    assert result is mock_response


def test_sync_stream(
    call_instance: llm.calls.ContextCall,
    mock_llm: Mock,
    mock_stream_response: Mock,
    toolkit: llm.ContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that ContextCall.stream passes parameters correctly to model.stream."""
    mock_llm.context_stream.return_value = mock_stream_response

    result = call_instance.stream(context, "sazed", title="keeper")

    mock_llm.context_stream.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=toolkit.tools,
        format=None,
        ctx=context,
    )
    assert result is mock_stream_response


def test_sync_stream_with_format(
    call_instance_with_format: llm.calls.ContextCall,
    mock_llm: Mock,
    mock_stream_response: Mock,
    toolkit: llm.ContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that ContextCall.stream with format passes parameters correctly to model.stream."""
    mock_llm.context_stream.return_value = mock_stream_response

    result = call_instance_with_format.stream(context, "sazed", title="keeper")

    mock_llm.context_stream.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=toolkit.tools,
        format=Format,
        ctx=context,
    )
    assert result is mock_stream_response


@pytest.mark.asyncio
async def test_async_dunder_call(
    async_call_instance: llm.calls.AsyncContextCall,
    mock_llm: Mock,
    mock_response: Mock,
    async_toolkit: llm.AsyncContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that AsyncContextCall.__call__ passes parameters correctly to model.call_async."""
    mock_llm.context_call_async = AsyncMock(return_value=mock_response)

    result = await async_call_instance(context, "sazed", title="keeper")

    mock_llm.context_call_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=async_toolkit.tools,
        format=None,
        ctx=context,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_async_dunder_call_with_format(
    async_call_instance_with_format: llm.calls.AsyncContextCall,
    mock_llm: Mock,
    mock_response: Mock,
    async_toolkit: llm.AsyncContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that AsyncContextCall.__call__ with format passes parameters correctly to model.call_async."""
    mock_llm.context_call_async = AsyncMock(return_value=mock_response)

    result = await async_call_instance_with_format(context, "sazed", title="keeper")

    mock_llm.context_call_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=async_toolkit.tools,
        format=Format,
        ctx=context,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_async_call_method(
    async_call_instance: llm.calls.AsyncContextCall,
    mock_llm: Mock,
    mock_response: Mock,
    async_toolkit: llm.AsyncContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that AsyncContextCall.call passes parameters correctly to model.call_async."""
    mock_llm.context_call_async = AsyncMock(return_value=mock_response)

    result = await async_call_instance.call(context, "sazed", title="keeper")

    mock_llm.context_call_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=async_toolkit.tools,
        format=None,
        ctx=context,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_async_call_method_with_format(
    async_call_instance_with_format: llm.calls.AsyncContextCall,
    mock_llm: Mock,
    mock_response: Mock,
    async_toolkit: llm.AsyncContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that AsyncContextCall.call with format passes parameters correctly to model.call_async."""
    mock_llm.context_call_async = AsyncMock(return_value=mock_response)

    result = await async_call_instance_with_format.call(
        context, "sazed", title="keeper"
    )

    mock_llm.context_call_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=async_toolkit.tools,
        format=Format,
        ctx=context,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_async_stream(
    async_call_instance: llm.calls.AsyncContextCall,
    mock_llm: Mock,
    mock_async_stream_response: Mock,
    async_toolkit: llm.AsyncContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that AsyncContextCall.stream passes parameters correctly to model.stream_async."""
    mock_llm.context_stream_async = AsyncMock(return_value=mock_async_stream_response)

    result = await async_call_instance.stream(context, "sazed", title="keeper")

    mock_llm.context_stream_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=async_toolkit.tools,
        format=None,
        ctx=context,
    )
    assert result is mock_async_stream_response


@pytest.mark.asyncio
async def test_async_stream_with_format(
    async_call_instance_with_format: llm.calls.AsyncContextCall,
    mock_llm: Mock,
    mock_async_stream_response: Mock,
    async_toolkit: llm.AsyncContextToolkit[int],
    context: llm.Context[int],
) -> None:
    """Test that AsyncContextCall.stream with format passes parameters correctly to model.stream_async."""
    mock_llm.context_stream_async = AsyncMock(return_value=mock_async_stream_response)

    result = await async_call_instance_with_format.stream(
        context, "sazed", title="keeper"
    )

    mock_llm.context_stream_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed (42)")],
        tools=async_toolkit.tools,
        format=Format,
        ctx=context,
    )
    assert result is mock_async_stream_response
