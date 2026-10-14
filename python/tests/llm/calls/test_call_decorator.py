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


def test_call_rejects_unknown_keyword_arguments() -> None:
    """Test that llm.call() rejects unknown keyword arguments at decoration time."""
    with pytest.raises(
        TypeError,
        match=r"llm\.call\(\) got unexpected keyword argument\(s\): nonsense_kwarg, provider\.",
    ) as exc_info:
        llm.call(model="openai/gpt-4o-mini", provider="openai", nonsense_kwarg=123)  # pyright: ignore[reportCallIssue]

    assert "Note that 'provider' is no longer a parameter" in str(exc_info.value)


def test_call_rejects_removed_provider_kwarg() -> None:
    """Test that passing provider as a keyword argument is rejected with migration note."""
    with pytest.raises(TypeError, match="provider") as exc_info:
        llm.call(provider="openai", model="gpt-4o-mini")  # pyright: ignore[reportCallIssue]

    assert "Note that 'provider' is no longer a parameter" in str(exc_info.value)


def test_call_rejects_typo_in_params() -> None:
    """Test that typos in param names are rejected at decoration time."""
    with pytest.raises(
        TypeError,
        match=r"llm\.call\(\) got unexpected keyword argument\(s\): temp_val\.",
    ):
        llm.call("openai/gpt-4o-mini", temp_val=0.7)  # pyright: ignore[reportCallIssue]


def test_call_rejects_params_when_model_instance_provided() -> None:
    """Test that llm.call() rejects parameters when a Model instance is provided."""
    m = llm.Model("openai/gpt-4o-mini")
    with pytest.raises(
        TypeError,
        match="Parameters cannot be passed when providing a Model instance",
    ):
        llm.call(m, temperature=0.7)  # pyright: ignore[reportArgumentType]


def test_call_accepts_valid_params() -> None:
    """Test that llm.call() accepts valid parameters."""

    @llm.call("openai/gpt-4o-mini", temperature=0.7, max_tokens=100)
    def my_call(q: str) -> str:
        return q

    assert isinstance(my_call, llm.Call)
