"""Tests for the call decorator function."""

from unittest.mock import Mock

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm


class Format(BaseModel):
    """Test format for structured responses."""

    value: str


@pytest.fixture
def tools() -> list[llm.Tool]:
    """Create a mock tool for testing."""

    @llm.tool
    def tool() -> int:
        return 42

    return [tool]


@pytest.fixture
def async_tools() -> list[llm.AsyncTool]:
    """Create a mock tool for testing."""

    @llm.tool
    async def tool() -> int:
        return 42

    return [tool]


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock client for testing."""
    return Mock()


@pytest.fixture
def params() -> llm.clients.BaseParams:
    return {"temperature": 0.7, "max_tokens": 100}


def test_call_decorator_creation_openai(
    tools: list[llm.Tool], mock_client: Mock, params: llm.clients.BaseParams
) -> None:
    """Test that call decorator creates CallDecorator with correct parameters for OpenAI."""

    decorator = llm.call(
        provider="openai",
        model="gpt-4o-mini",
        tools=tools,
        format=Format,
        client=mock_client,
        **params,
    )

    assert decorator.tools is tools
    assert decorator.format is Format
    assert decorator.model.client is mock_client
    assert decorator.model.provider == "openai"
    assert decorator.model.model == "gpt-4o-mini"
    assert decorator.model.params == params


def test_creating_sync_call(
    tools: list[llm.Tool], mock_client: Mock, params: llm.clients.BaseParams
) -> None:
    """Test that call decorator creates CallDecorator with correct parameters for OpenAI."""

    def prompt() -> str:
        return "Please recommend a fantasy book."

    call = llm.call(
        provider="openai",
        model="gpt-4o-mini",
        tools=tools,
        format=Format,
        client=mock_client,
        **params,
    )(prompt)

    assert isinstance(call, llm.calls.Call)

    assert call.model.client is mock_client
    assert call.model.provider == "openai"
    assert call.model.model == "gpt-4o-mini"
    assert call.model.params == params

    assert call.toolkit == llm.Toolkit(tools=tools)
    assert call.format is Format
    assert call.fn is prompt


@pytest.mark.asyncio
async def test_creating_async_call(
    async_tools: list[llm.AsyncTool], mock_client: Mock, params: llm.clients.BaseParams
) -> None:
    """Test that call decorator creates CallDecorator with correct parameters for OpenAI."""

    async def async_prompt() -> str:
        return "Please recommend a fantasy book."

    call = llm.call(
        provider="openai",
        model="gpt-4o-mini",
        tools=async_tools,
        format=Format,
        client=mock_client,
        **params,
    )(async_prompt)

    assert isinstance(call, llm.calls.AsyncCall)

    assert call.model.client is mock_client
    assert call.model.provider == "openai"
    assert call.model.model == "gpt-4o-mini"
    assert call.model.params == params

    assert call.toolkit == llm.AsyncToolkit(tools=async_tools)
    assert call.format is Format
    assert call.fn is async_prompt


@pytest.mark.vcr()
def test_call_decorator_e2e_anthropic() -> None:
    @llm.call(provider="anthropic", model="claude-sonnet-4-0")
    def call() -> str:
        return "Please recommend a fantasy book. Answer concisely in just one sentence."

    response = call()
    assert response.pretty() == snapshot(
        'I recommend "The Name of the Wind" by Patrick Rothfuss for its beautiful prose and compelling story of Kvothe, a legendary figure recounting his youth as a gifted student of magic.'
    )


@pytest.mark.vcr()
def test_call_decorator_e2e_google() -> None:
    @llm.call(provider="google", model="gemini-2.0-flash")
    def call() -> str:
        return "Please recommend a fantasy book. Answer concisely in just one sentence."

    response = call()
    assert response.pretty() == snapshot(
        'For a captivating blend of political intrigue, epic battles, and compelling characters, read "The Lies of Locke Lamora" by Scott Lynch.\n'
    )


@pytest.mark.vcr()
def test_call_decorator_e2e_openai() -> None:
    @llm.call(provider="openai", model="gpt-4o-mini")
    def call() -> str:
        return "Please recommend a fantasy book. Answer concisely in just one sentence."

    response = call()
    assert response.pretty() == snapshot(
        'I recommend "The Name of the Wind" by Patrick Rothfuss for its rich storytelling and captivating protagonist.'
    )


def test_value_error_invalid_provider() -> None:
    with pytest.raises(ValueError, match="Unknown provider: nonexistent"):
        llm.call(provider="nonexistent", model="gpt-4o-mini")  # pyright: ignore[reportCallIssue, reportArgumentType]
