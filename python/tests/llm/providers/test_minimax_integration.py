"""Integration tests for MiniMax provider with the Mirascope framework.

These tests verify MiniMax works through the provider registry and call decorator.
They require MINIMAX_API_KEY to be set in the environment.
"""

import os

import pytest

from mirascope import llm
from mirascope.llm.providers.minimax.provider import MiniMaxProvider
from mirascope.llm.providers.provider_registry import (
    get_provider_for_model,
    provider_singleton,
    reset_provider_registry,
)


@pytest.fixture(autouse=True)
def _clean_registry() -> None:
    """Reset provider registry before each test."""
    reset_provider_registry()


@pytest.fixture
def minimax_api_key() -> str:
    """Get MINIMAX_API_KEY from environment, skip if not set."""
    key = os.environ.get("MINIMAX_API_KEY", "")
    if not key:
        pytest.skip("MINIMAX_API_KEY not set")
    return key


def test_provider_singleton_creates_minimax() -> None:
    """Test provider_singleton returns a MiniMaxProvider."""
    provider = provider_singleton("minimax", api_key="test-key")
    assert isinstance(provider, MiniMaxProvider)
    assert provider.id == "minimax"


def test_auto_register_minimax_scope(minimax_api_key: str) -> None:
    """Test that minimax/ scope is auto-registered from DEFAULT_AUTO_REGISTER_SCOPES."""
    provider = get_provider_for_model("minimax/MiniMax-M2.7")
    assert isinstance(provider, MiniMaxProvider)


def test_minimax_call_sync(minimax_api_key: str) -> None:
    """Test synchronous call to MiniMax via @llm.call decorator."""

    @llm.call("minimax/MiniMax-M2.7")
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}? Reply with just the number."

    response = add_numbers(100, 23)
    assert "123" in response.pretty()


@pytest.mark.asyncio
async def test_minimax_call_async(minimax_api_key: str) -> None:
    """Test asynchronous call to MiniMax via @llm.call decorator."""

    @llm.call("minimax/MiniMax-M2.7")
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}? Reply with just the number."

    response = await add_numbers(200, 45)
    assert "245" in response.pretty()


def test_minimax_stream_sync(minimax_api_key: str) -> None:
    """Test synchronous streaming from MiniMax."""

    @llm.call("minimax/MiniMax-M2.7")
    def greet() -> str:
        return "Say hello in one word."

    response = greet.stream()
    response.finish()
    assert len(response.pretty()) > 0
