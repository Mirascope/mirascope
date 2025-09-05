"""Tests for the LLM class."""

from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import BaseModel

from mirascope import llm


class Format(BaseModel): ...


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock client for testing."""
    return Mock()


@pytest.fixture
def mock_response() -> Mock:
    """Create a mock response for testing."""
    return Mock(spec=llm.Response)


@pytest.fixture
def mock_stream_response() -> Mock:
    """Create a mock stream response for testing."""
    return Mock(spec=llm.StreamResponse)


@pytest.fixture
def mock_async_stream_response() -> Mock:
    """Create a mock async stream response for testing."""
    return Mock(spec=llm.AsyncStreamResponse)


@pytest.fixture
def params() -> llm.clients.OpenAIParams:
    """Create example OpenAI parameters for testing."""
    return llm.clients.OpenAIParams(temperature=0.5)


@pytest.fixture
def messages() -> list[llm.messages.Message]:
    """Create example messages for testing."""
    return [llm.messages.user("Hello")]


@pytest.fixture
def tools() -> list[llm.Tool]:
    """Create an example tool for testing."""

    @llm.tool
    def tool() -> int:
        return 42

    return [tool]


@pytest.fixture
def async_tools() -> list[llm.AsyncTool]:
    """Create an example tool for testing."""

    @llm.tool
    async def tool() -> int:
        return 42

    return [tool]


@pytest.fixture
def mocked_llm(mock_client: Mock, params: llm.clients.OpenAIParams) -> llm.Model:
    """Create a test LLM instance with mock client."""
    return llm.model(
        provider="openai",
        model_id="gpt-4o-mini",
        client=mock_client,
        **params,
    )


def test_cant_use_init() -> None:
    with pytest.raises(TypeError, match="llm.model"):
        llm.Model()


def test_create_provides_client() -> None:
    """Test that a client is created for the LLM if not provided"""
    test_llm = llm.model(provider="openai", model_id="gpt-4o")
    assert isinstance(test_llm.client, llm.clients.OpenAIClient)


def test_call(
    mocked_llm: llm.Model,
    mock_client: Mock,
    mock_response: Mock,
    params: llm.clients.OpenAIParams,
    messages: list[llm.messages.Message],
    tools: list[llm.Tool],
) -> None:
    """Test that call method passes parameters correctly to client.call."""
    mock_client.call.return_value = mock_response

    result = mocked_llm.call(messages=messages, tools=tools)

    mock_client.call.assert_called_once_with(
        model_id="gpt-4o-mini",
        messages=messages,
        tools=tools,
        params=params,
    )
    assert result is mock_response


def test_structured_call(
    mocked_llm: llm.Model,
    mock_client: Mock,
    mock_response: Mock,
    params: llm.clients.OpenAIParams,
    messages: list[llm.messages.Message],
    tools: list[llm.Tool],
) -> None:
    """Test that call method passes format parameter correctly to client.call."""
    mock_client.call.return_value = mock_response

    result = mocked_llm.call(messages=messages, tools=tools, format=Format)

    mock_client.call.assert_called_once_with(
        model_id="gpt-4o-mini",
        messages=messages,
        tools=tools,
        params=params,
        format=Format,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_call_async(
    mocked_llm: llm.Model,
    mock_client: Mock,
    mock_response: Mock,
    params: llm.clients.OpenAIParams,
    messages: list[llm.messages.Message],
    async_tools: list[llm.AsyncTool],
) -> None:
    """Test that call_async method passes parameters correctly to client.call_async."""
    mock_client.call_async = AsyncMock(return_value=mock_response)

    result = await mocked_llm.call_async(messages=messages, tools=async_tools)

    mock_client.call_async.assert_called_once_with(
        model_id="gpt-4o-mini",
        messages=messages,
        tools=async_tools,
        params=params,
    )
    assert result is mock_response


@pytest.mark.asyncio
async def test_structured_call_async(
    mocked_llm: llm.Model,
    mock_client: Mock,
    mock_response: Mock,
    params: llm.clients.OpenAIParams,
    messages: list[llm.messages.Message],
    async_tools: list[llm.AsyncTool],
) -> None:
    """Test that call_async method passes format parameters correctly to client.call_async."""
    mock_client.call_async = AsyncMock(return_value=mock_response)

    result = await mocked_llm.call_async(
        messages=messages, tools=async_tools, format=Format
    )

    mock_client.call_async.assert_called_once_with(
        model_id="gpt-4o-mini",
        messages=messages,
        tools=async_tools,
        params=params,
        format=Format,
    )
    assert result is mock_response


def test_stream(
    mocked_llm: llm.Model,
    mock_client: Mock,
    mock_stream_response: Mock,
    params: llm.clients.OpenAIParams,
    messages: list[llm.messages.Message],
    tools: list[llm.Tool],
) -> None:
    """Test that stream method passes parameters correctly to client.stream."""
    mock_client.stream.return_value = mock_stream_response

    result = mocked_llm.stream(messages=messages, tools=tools)

    mock_client.stream.assert_called_once_with(
        model_id="gpt-4o-mini",
        messages=messages,
        tools=tools,
        params=params,
    )
    assert result is mock_stream_response


def test_structured_stream(
    mocked_llm: llm.Model,
    mock_client: Mock,
    mock_stream_response: Mock,
    params: llm.clients.OpenAIParams,
    messages: list[llm.messages.Message],
    tools: list[llm.Tool],
) -> None:
    """Test that stream method passes format parameters correctly to client.stream."""
    mock_client.stream.return_value = mock_stream_response

    result = mocked_llm.stream(messages=messages, tools=tools, format=Format)

    mock_client.stream.assert_called_once_with(
        model_id="gpt-4o-mini",
        messages=messages,
        tools=tools,
        params=params,
        format=Format,
    )
    assert result is mock_stream_response


@pytest.mark.asyncio
async def test_stream_async(
    mocked_llm: llm.Model,
    mock_client: Mock,
    mock_async_stream_response: Mock,
    params: llm.clients.OpenAIParams,
    messages: list[llm.messages.Message],
    async_tools: list[llm.AsyncTool],
) -> None:
    """Test that stream_async method passes parameters correctly to client.stream_async."""
    mock_client.stream_async = AsyncMock(return_value=mock_async_stream_response)

    result = await mocked_llm.stream_async(messages=messages, tools=async_tools)

    mock_client.stream_async.assert_called_once_with(
        model_id="gpt-4o-mini",
        messages=messages,
        tools=async_tools,
        params=params,
    )
    assert result is mock_async_stream_response


@pytest.mark.asyncio
async def test_structured_stream_async(
    mocked_llm: llm.Model,
    mock_client: Mock,
    mock_async_stream_response: Mock,
    params: llm.clients.OpenAIParams,
    messages: list[llm.messages.Message],
    async_tools: list[llm.AsyncTool],
) -> None:
    """Test that stream_async method passes format parameters correctly to client.stream_async."""
    mock_client.stream_async = AsyncMock(return_value=mock_async_stream_response)

    result = await mocked_llm.stream_async(
        messages=messages, tools=async_tools, format=Format
    )

    mock_client.stream_async.assert_called_once_with(
        model_id="gpt-4o-mini",
        messages=messages,
        tools=async_tools,
        params=params,
        format=Format,
    )
    assert result is mock_async_stream_response


def test_context_manager() -> None:
    assert llm.models.get_model_from_context() is None

    with llm.models.model(provider="openai", model_id="gpt-4o-mini") as llm_outer:
        assert isinstance(llm_outer, llm.models.Model)
        assert llm_outer.provider == "openai"
        assert llm.models.get_model_from_context() == llm_outer

        with llm.models.model(
            provider="anthropic", model_id="claude-sonnet-4-0"
        ) as llm_inner:
            assert isinstance(llm_inner, llm.models.Model)
            assert llm_inner.provider == "anthropic"
            assert llm.models.get_model_from_context() == llm_inner

        assert llm.models.get_model_from_context() == llm_outer

    assert llm.models.get_model_from_context() is None
