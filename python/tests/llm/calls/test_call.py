"""Tests for the Call and AsyncCall classes."""

from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import BaseModel

from mirascope import llm


class Format(BaseModel):
    """Test format for structured responses."""

    ...


@pytest.fixture
def mock_llm() -> Mock:
    """Create a mock LLM for testing."""
    return Mock(spec=llm.LLM)


@pytest.fixture
def toolkit() -> llm.Toolkit:
    """Create a mock toolkit for testing."""

    @llm.tool
    def tool() -> int:
        return 42

    toolkit = llm.Toolkit(tools=[tool])
    return toolkit


@pytest.fixture
def async_toolkit() -> llm.AsyncToolkit:
    """Create a mock async toolkit for testing."""

    @llm.tool
    async def async_tool() -> int:
        return 42

    toolkit = llm.AsyncToolkit(tools=[async_tool])
    return toolkit


@pytest.fixture
def mock_prompt() -> llm.prompts.Prompt:
    """Create a mock prompt function."""

    def prompt(name: str, *, title: str = "dr") -> str:
        return f"hi {title} {name}"

    return prompt


@pytest.fixture
def mock_async_prompt() -> llm.prompts.AsyncPrompt:
    """Create a mock async prompt function."""

    async def prompt(name: str, *, title: str = "dr") -> str:
        return f"hi {title} {name}"

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
    mock_llm: Mock, toolkit: llm.Toolkit, mock_prompt: llm.prompts.Prompt
) -> llm.calls.Call:
    """Create a Call instance for testing."""
    return llm.calls.Call(
        default_model=mock_llm, toolkit=toolkit, format=None, fn=mock_prompt
    )


@pytest.fixture
def call_instance_with_format(
    mock_llm: Mock, toolkit: llm.Toolkit, mock_prompt: llm.prompts.Prompt
) -> llm.calls.Call[..., Format]:
    """Create a Call instance with format for testing."""
    return llm.calls.Call(
        default_model=mock_llm, toolkit=toolkit, format=Format, fn=mock_prompt
    )


@pytest.fixture
def async_call_instance(
    mock_llm: Mock,
    async_toolkit: llm.AsyncToolkit,
    mock_async_prompt: llm.prompts.AsyncPrompt,
) -> llm.calls.AsyncCall:
    """Create an AsyncCall instance for testing."""
    return llm.calls.AsyncCall(
        default_model=mock_llm, toolkit=async_toolkit, format=None, fn=mock_async_prompt
    )


@pytest.fixture
def async_call_instance_with_format(
    mock_llm: Mock,
    async_toolkit: llm.AsyncToolkit,
    mock_async_prompt: llm.prompts.AsyncPrompt,
) -> llm.calls.AsyncCall[..., Format]:
    """Create an AsyncCall instance with format for testing."""
    return llm.calls.AsyncCall(
        default_model=mock_llm,
        toolkit=async_toolkit,
        format=Format,
        fn=mock_async_prompt,
    )


@pytest.fixture
def previous_response() -> Mock:
    """Create a mock previous response for resume tests."""
    mock_response = Mock()
    mock_response.messages = [
        llm.messages.user("first message"),
        llm.messages.assistant("first response"),
    ]
    return mock_response


@pytest.fixture
def expected_resume_messages() -> list[llm.messages.Message]:
    """Create expected messages for resume tests."""
    return [
        llm.messages.user("first message"),
        llm.messages.assistant("first response"),
        llm.messages.user("follow up message"),
    ]


def test_call_dunder_call(
    call_instance: llm.calls.Call,
    mock_llm: Mock,
    mock_response: Mock,
    toolkit: llm.Toolkit,
) -> None:
    """Test that Call.__call__ passes parameters correctly to model.call."""
    mock_llm.call.return_value = mock_response

    result = call_instance("sazed", title="keeper")

    mock_llm.call.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=toolkit.tools,
        format=None,
    )
    assert result is mock_response


def test_call_dunder_call_with_format(
    call_instance_with_format: llm.calls.Call,
    mock_llm: Mock,
    mock_response: Mock,
    toolkit: llm.Toolkit,
) -> None:
    """Test that Call.__call__ with format passes parameters correctly to model.call."""
    mock_llm.call.return_value = mock_response

    result = call_instance_with_format("sazed", title="keeper")

    mock_llm.call.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=toolkit.tools,
        format=Format,
    )
    assert result is mock_response


def test_call_call_method(
    call_instance: llm.calls.Call,
    mock_llm: Mock,
    mock_response: Mock,
    toolkit: llm.Toolkit,
) -> None:
    """Test that Call.call passes parameters correctly to model.call."""
    mock_llm.call.return_value = mock_response

    result = call_instance.call("sazed", title="keeper")

    mock_llm.call.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=toolkit.tools,
        format=None,
    )
    assert result is mock_response


def test_call_call_method_with_format(
    call_instance_with_format: llm.calls.Call,
    mock_llm: Mock,
    mock_response: Mock,
    toolkit: llm.Toolkit,
) -> None:
    """Test that Call.call with format passes parameters correctly to model.call."""
    mock_llm.call.return_value = mock_response

    result = call_instance_with_format.call("sazed", title="keeper")

    mock_llm.call.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=toolkit.tools,
        format=Format,
    )
    assert result is mock_response


def test_call_stream(
    call_instance: llm.calls.Call,
    mock_llm: Mock,
    mock_stream_response: Mock,
    toolkit: llm.Toolkit,
) -> None:
    """Test that Call.stream passes parameters correctly to model.stream."""
    mock_llm.stream.return_value = mock_stream_response

    result = call_instance.stream("sazed", title="keeper")

    mock_llm.stream.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=toolkit.tools,
        format=None,
    )
    assert result is mock_stream_response


def test_call_stream_with_format(
    call_instance_with_format: llm.calls.Call,
    mock_llm: Mock,
    mock_stream_response: Mock,
    toolkit: llm.Toolkit,
) -> None:
    """Test that Call.stream with format passes parameters correctly to model.stream."""
    mock_llm.stream.return_value = mock_stream_response

    result = call_instance_with_format.stream("sazed", title="keeper")

    mock_llm.stream.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=toolkit.tools,
        format=Format,
    )
    assert result is mock_stream_response


def test_call_resume(
    call_instance: llm.calls.Call,
    mock_llm: Mock,
    mock_response: Mock,
    toolkit: llm.Toolkit,
    previous_response: Mock,
    expected_resume_messages: list[llm.messages.Message],
) -> None:
    """Test that Call.resume continues conversation correctly."""
    mock_llm.call.return_value = mock_response

    result = call_instance.resume(previous_response, "follow up message")

    mock_llm.call.assert_called_once_with(
        messages=expected_resume_messages,
        tools=toolkit.tools,
        format=None,
    )
    assert result is mock_response


def test_call_resume_with_format(
    call_instance_with_format: llm.calls.Call,
    mock_llm: Mock,
    mock_response: Mock,
    toolkit: llm.Toolkit,
    previous_response: Mock,
    expected_resume_messages: list[llm.messages.Message],
) -> None:
    """Test that Call.resume with format continues conversation correctly."""
    mock_llm.call.return_value = mock_response

    result = call_instance_with_format.resume(previous_response, "follow up message")

    mock_llm.call.assert_called_once_with(
        messages=expected_resume_messages,
        tools=toolkit.tools,
        format=Format,
    )
    assert result is mock_response


def test_call_resume_stream(
    call_instance: llm.calls.Call,
    mock_llm: Mock,
    mock_stream_response: Mock,
    toolkit: llm.Toolkit,
    previous_response: Mock,
    expected_resume_messages: list[llm.messages.Message],
) -> None:
    """Test that Call.resume_stream continues conversation correctly."""
    mock_llm.stream.return_value = mock_stream_response

    result = call_instance.resume_stream(previous_response, "follow up message")

    mock_llm.stream.assert_called_once_with(
        messages=expected_resume_messages,
        tools=toolkit.tools,
        format=None,
    )
    assert result is mock_stream_response


def test_call_resume_stream_with_format(
    call_instance_with_format: llm.calls.Call,
    mock_llm: Mock,
    mock_stream_response: Mock,
    toolkit: llm.Toolkit,
    previous_response: Mock,
    expected_resume_messages: list[llm.messages.Message],
) -> None:
    """Test that Call.resume_stream with format continues conversation correctly."""
    mock_llm.stream.return_value = mock_stream_response

    result = call_instance_with_format.resume_stream(
        previous_response, "follow up message"
    )

    mock_llm.stream.assert_called_once_with(
        messages=expected_resume_messages,
        tools=toolkit.tools,
        format=Format,
    )
    assert result is mock_stream_response


@pytest.mark.asyncio
async def test_async_call_dunder_call(
    async_call_instance: llm.calls.AsyncCall,
    mock_llm: Mock,
    mock_response: Mock,
    async_toolkit: llm.AsyncToolkit,
) -> None:
    """Test that AsyncCall.__call__ passes parameters correctly to model.call_async."""
    mock_llm.call_async = AsyncMock(return_value=mock_response)

    result = await async_call_instance("sazed", title="keeper")

    mock_llm.call_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=async_toolkit.tools,
        format=None,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_async_call_dunder_call_with_format(
    async_call_instance_with_format: llm.calls.AsyncCall,
    mock_llm: Mock,
    mock_response: Mock,
    async_toolkit: llm.AsyncToolkit,
) -> None:
    """Test that AsyncCall.__call__ with format passes parameters correctly to model.call_async."""
    mock_llm.call_async = AsyncMock(return_value=mock_response)

    result = await async_call_instance_with_format("sazed", title="keeper")

    mock_llm.call_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=async_toolkit.tools,
        format=Format,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_async_call_call_method(
    async_call_instance: llm.calls.AsyncCall,
    mock_llm: Mock,
    mock_response: Mock,
    async_toolkit: llm.AsyncToolkit,
) -> None:
    """Test that AsyncCall.call passes parameters correctly to model.call_async."""
    mock_llm.call_async = AsyncMock(return_value=mock_response)

    result = await async_call_instance.call("sazed", title="keeper")

    mock_llm.call_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=async_toolkit.tools,
        format=None,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_async_call_call_method_with_format(
    async_call_instance_with_format: llm.calls.AsyncCall,
    mock_llm: Mock,
    mock_response: Mock,
    async_toolkit: llm.AsyncToolkit,
) -> None:
    """Test that AsyncCall.call with format passes parameters correctly to model.call_async."""
    mock_llm.call_async = AsyncMock(return_value=mock_response)

    result = await async_call_instance_with_format.call("sazed", title="keeper")

    mock_llm.call_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=async_toolkit.tools,
        format=Format,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_async_call_stream(
    async_call_instance: llm.calls.AsyncCall,
    mock_llm: Mock,
    mock_async_stream_response: Mock,
    async_toolkit: llm.AsyncToolkit,
) -> None:
    """Test that AsyncCall.stream passes parameters correctly to model.stream_async."""
    mock_llm.stream_async = AsyncMock(return_value=mock_async_stream_response)

    result = await async_call_instance.stream("sazed", title="keeper")

    mock_llm.stream_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=async_toolkit.tools,
        format=None,
    )
    assert result is mock_async_stream_response


@pytest.mark.asyncio
async def test_async_call_stream_with_format(
    async_call_instance_with_format: llm.calls.AsyncCall,
    mock_llm: Mock,
    mock_async_stream_response: Mock,
    async_toolkit: llm.AsyncToolkit,
) -> None:
    """Test that AsyncCall.stream with format passes parameters correctly to model.stream_async."""
    mock_llm.stream_async = AsyncMock(return_value=mock_async_stream_response)

    result = await async_call_instance_with_format.stream("sazed", title="keeper")

    mock_llm.stream_async.assert_called_once_with(
        messages=[llm.messages.user("hi keeper sazed")],
        tools=async_toolkit.tools,
        format=Format,
    )
    assert result is mock_async_stream_response


@pytest.mark.asyncio
async def test_async_call_resume(
    async_call_instance: llm.calls.AsyncCall,
    mock_llm: Mock,
    mock_response: Mock,
    async_toolkit: llm.AsyncToolkit,
    previous_response: Mock,
    expected_resume_messages: list[llm.messages.Message],
) -> None:
    """Test that AsyncCall.resume continues conversation correctly."""
    mock_llm.call_async = AsyncMock(return_value=mock_response)

    result = await async_call_instance.resume(previous_response, "follow up message")

    mock_llm.call_async.assert_called_once_with(
        messages=expected_resume_messages,
        tools=async_toolkit.tools,
        format=None,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_async_call_resume_with_format(
    async_call_instance_with_format: llm.calls.AsyncCall,
    mock_llm: Mock,
    mock_response: Mock,
    async_toolkit: llm.AsyncToolkit,
    previous_response: Mock,
    expected_resume_messages: list[llm.messages.Message],
) -> None:
    """Test that AsyncCall.resume with format continues conversation correctly."""
    mock_llm.call_async = AsyncMock(return_value=mock_response)

    result = await async_call_instance_with_format.resume(
        previous_response, "follow up message"
    )

    mock_llm.call_async.assert_called_once_with(
        messages=expected_resume_messages,
        tools=async_toolkit.tools,
        format=Format,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_async_call_resume_stream(
    async_call_instance: llm.calls.AsyncCall,
    mock_llm: Mock,
    mock_async_stream_response: Mock,
    async_toolkit: llm.AsyncToolkit,
    previous_response: Mock,
    expected_resume_messages: list[llm.messages.Message],
) -> None:
    """Test that AsyncCall.resume_stream continues conversation correctly."""
    mock_llm.stream_async = AsyncMock(return_value=mock_async_stream_response)

    result = await async_call_instance.resume_stream(
        previous_response, "follow up message"
    )

    mock_llm.stream_async.assert_called_once_with(
        messages=expected_resume_messages,
        tools=async_toolkit.tools,
        format=None,
    )
    assert result is mock_async_stream_response


@pytest.mark.asyncio
async def test_async_call_resume_stream_with_format(
    async_call_instance_with_format: llm.calls.AsyncCall,
    mock_llm: Mock,
    mock_async_stream_response: Mock,
    async_toolkit: llm.AsyncToolkit,
    previous_response: Mock,
    expected_resume_messages: list[llm.messages.Message],
) -> None:
    """Test that AsyncCall.resume_stream with format continues conversation correctly."""
    mock_llm.stream_async = AsyncMock(return_value=mock_async_stream_response)

    result = await async_call_instance_with_format.resume_stream(
        previous_response, "follow up message"
    )

    mock_llm.stream_async.assert_called_once_with(
        messages=expected_resume_messages,
        tools=async_toolkit.tools,
        format=Format,
    )
    assert result is mock_async_stream_response
