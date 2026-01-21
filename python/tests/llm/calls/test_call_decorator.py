"""Simple smoke tests for the call decorator."""

import pytest

from mirascope import llm


class TestCallDecoratorSmokeTests:
    """Smoke tests for each call type.

    This just checks that we're returning the correct Call type as a general
    smoke test. We don't need to unit test tools, format, etc, because the e2e
    tests make extensive use of the `llm.call` decorator, so we get full
    coverage of the relevant code.
    """

    def test_sync_call_creation(self) -> None:
        """Test that a sync function creates a Call."""

        @llm.call("openai/gpt-4o-mini")
        def my_call(question: str) -> str:
            return f"Answer this: {question}"

        assert isinstance(my_call, llm.Call)

    @pytest.mark.asyncio
    async def test_async_call_creation(self) -> None:
        """Test that an async function creates an AsyncCall."""

        @llm.call("openai/gpt-4o-mini")
        async def my_async_call(question: str) -> str:
            return f"Answer this: {question}"

        assert isinstance(my_async_call, llm.AsyncCall)

    def test_context_call_creation(self) -> None:
        """Test that a sync function with ctx parameter creates a ContextCall."""

        @llm.call("openai/gpt-4o-mini")
        def my_context_call(ctx: llm.Context[str], question: str) -> str:
            return f"Context: {ctx.deps}. Question: {question}"

        assert isinstance(my_context_call, llm.ContextCall)

    @pytest.mark.asyncio
    async def test_async_context_call_creation(self) -> None:
        """Test that an async function with ctx parameter creates an AsyncContextCall."""

        @llm.call("openai/gpt-4o-mini")
        async def my_async_context_call(ctx: llm.Context[str], question: str) -> str:
            return f"Context: {ctx.deps}. Question: {question}"

        assert isinstance(my_async_context_call, llm.AsyncContextCall)
