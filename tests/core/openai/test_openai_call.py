"""Tests the mirascope.core.openai.openai_call module."""

import pytest


def test_openai_call_decorator_call() -> None:
    """Tests the `openai_call` decorator for a standard call."""
    pass


@pytest.mark.asyncio
async def test_openai_call_decorator_call_async() -> None:
    """Tests the `openai_call` decorator for an async call."""
    pass


def test_openai_call_decorator_stream() -> None:
    """Tests the `openai_call` decorator for a standard stream."""
    pass


@pytest.mark.asyncio
async def test_openai_call_decorator_stream_async() -> None:
    """Tests the `openai_call` decorator for a standard stream."""
    pass
