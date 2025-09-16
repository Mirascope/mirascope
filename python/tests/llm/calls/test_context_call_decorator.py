"""Tests for the context_call decorator function."""

from typing import cast

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
def context_tools() -> list[llm.ContextTool]:
    """Create a mock context tool for testing."""

    @llm.tool
    def context_tool(ctx: llm.Context[int]) -> int:
        return ctx.deps

    return [context_tool]


@pytest.fixture
def async_tools() -> list[llm.AsyncTool]:
    """Create a mock async tool for testing."""

    @llm.tool
    async def async_tool() -> int:
        return 42

    return [async_tool]


@pytest.fixture
def async_context_tools() -> list[llm.AsyncContextTool]:
    """Create a mock async context tool for testing."""

    @llm.tool
    async def async_context_tool(ctx: llm.Context[int]) -> int:
        return ctx.deps

    return [async_context_tool]


@pytest.fixture
def params() -> llm.clients.BaseParams:
    return {"temperature": 0.7, "max_tokens": 100}


def test_context_call_decorator_creation_openai(
    context_tools: list[llm.ContextTool], params: llm.clients.BaseParams
) -> None:
    """Test that context_call decorator creates ContextCallDecorator with correct parameters for OpenAI."""

    decorator = llm.context_call(
        provider="openai",
        model_id="gpt-4o-mini",
        tools=context_tools,
        format=Format,
        **params,
    )

    assert decorator.tools is context_tools
    assert decorator.format is Format
    assert decorator.model.provider == "openai"
    assert decorator.model.model_id == "gpt-4o-mini"
    assert decorator.model.params == params


def test_creating_sync_context_call(
    context_tools: list[llm.ContextTool], params: llm.clients.BaseParams
) -> None:
    """Test that context_call decorator creates ContextCall with correct parameters."""

    def context_prompt(ctx: llm.Context[int]) -> str:
        return f"Please recommend a fantasy book. My context value is {ctx.deps}."

    call = llm.context_call(
        provider="openai",
        model_id="gpt-4o-mini",
        tools=context_tools,
        format=Format,
        **params,
    )(context_prompt)

    assert isinstance(call, llm.calls.ContextCall)

    assert call.model.provider == "openai"
    assert call.model.model_id == "gpt-4o-mini"
    assert call.model.params == params

    assert call.toolkit == llm.ContextToolkit(tools=context_tools)
    assert call.format is Format
    assert call.fn is context_prompt


@pytest.mark.asyncio
async def test_creating_async_context_call(
    async_context_tools: list[llm.AsyncContextTool], params: llm.clients.BaseParams
) -> None:
    """Test that context_call decorator creates AsyncContextCall with correct parameters."""

    async def async_context_prompt(ctx: llm.Context[int]) -> str:
        return f"Please recommend a fantasy book. My context value is {ctx.deps}."

    call = llm.context_call(
        provider="openai",
        model_id="gpt-4o-mini",
        tools=async_context_tools,
        format=Format,
        **params,
    )(async_context_prompt)

    assert isinstance(call, llm.calls.AsyncContextCall)

    assert call.model.provider == "openai"
    assert call.model.model_id == "gpt-4o-mini"
    assert call.model.params == params

    assert call.toolkit == llm.AsyncContextToolkit(tools=async_context_tools)
    assert call.format is Format
    assert call.fn is async_context_prompt


def test_context_call_decorator_with_mixed_tools(
    tools: list[llm.Tool], params: llm.clients.BaseParams
) -> None:
    """Test that context_call decorator works with regular tools too."""

    def context_prompt(ctx: llm.Context[int]) -> str:
        return f"Please recommend a fantasy book. My context value is {ctx.deps}."

    call = llm.context_call(
        provider="openai",
        model_id="gpt-4o-mini",
        tools=tools,
        format=Format,
        **params,
    )(context_prompt)

    assert isinstance(call, llm.calls.ContextCall)
    assert call.toolkit == llm.ContextToolkit(tools=tools)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "provider_and_model_id",
    [
        "openai:gpt-4o",
        "anthropic:claude-sonnet-4-0",
        "google:gemini-2.5-flash",
    ],
)
def test_context_call_decorator_e2e(
    provider_and_model_id: str,
) -> None:
    """End-to-end test of context_call decorator."""
    provider, model_id = provider_and_model_id.split(":")
    provider = cast(llm.clients.Provider, provider)

    @llm.context_call(provider=provider, model_id=model_id)
    def call(ctx: llm.Context[str]) -> str:
        return f"Please recommend a fantasy book based on my preference: {ctx.deps}. Answer concisely in just one sentence."

    context = llm.Context(deps="I love gothic fantasy horror")
    response = call(context)

    expected = snapshot(
        {
            "openai": 'You might enjoy "The Monstrous Tales" by Emma Jane Holloway, which weaves a haunting blend of gothic fantasy and horror.',
            "anthropic": 'I highly recommend **"The Thirteenth Tale" by Diane Setterfield**, a haunting gothic fantasy that weaves together dark family secrets, mysterious twins, and atmospheric Victorian horror in a decaying English mansion.',
            "google": "Read *Between Two Fires* by Christopher Buehlman for a dark, medieval epic filled with angels, demons, and grotesque horror.",
        }
    )

    assert response.pretty() == expected[provider]


@pytest.mark.vcr()
def test_context_call_decorator_e2e_model_override() -> None:
    ctx = llm.Context(deps="Who created you?")

    @llm.call(provider="openai", model_id="gpt-4o-mini")
    def call(ctx: llm.Context[str]) -> str:
        return f"Answer the question in just one word: {ctx.deps}."

    assert call(ctx).pretty() == snapshot("OpenAI.")
    with llm.model(provider="google", model_id="gemini-2.0-flash"):
        assert call(ctx).pretty() == snapshot("Google.\n")
        with llm.model(provider="anthropic", model_id="claude-sonnet-4-0"):
            assert call(ctx).pretty() == snapshot("Anthropic.")


def test_value_error_invalid_provider() -> None:
    """Test that invalid provider raises ValueError."""
    with pytest.raises(ValueError, match="Unknown provider: nonexistent"):
        llm.context_call(provider="nonexistent", model_id="gpt-4o-mini")  # pyright: ignore[reportCallIssue, reportArgumentType]
