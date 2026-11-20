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


class TestCallDecoratorUnknownKwargs:
    """Tests that unknown kwargs to `llm.call` are rejected at decoration time.

    Regression tests for https://github.com/Mirascope/mirascope/issues/2879:
    unknown keyword arguments (typos, removed parameters) used to be silently
    accepted and stored on the model, where providers ignored them.
    """

    def test_unknown_kwarg_raises_type_error(self) -> None:
        """Test that an unknown kwarg raises a TypeError naming the argument."""
        with pytest.raises(TypeError, match="nonsense_kwarg"):

            @llm.call("openai/gpt-4o-mini", nonsense_kwarg=123)  # type: ignore[call-arg]
            def my_call(question: str) -> str:
                return question

    def test_removed_provider_kwarg_has_model_id_hint(self) -> None:
        """Test that the removed `provider=` kwarg gets a model id hint."""
        with pytest.raises(TypeError) as exc_info:

            @llm.call("openai/gpt-4o-mini", provider="openai")  # type: ignore[call-arg]
            def my_call(question: str) -> str:
                return question

        assert "'provider'" in str(exc_info.value)
        assert "part of the model id" in str(exc_info.value)
        assert "openai/gpt-4o-mini" in str(exc_info.value)

    def test_misspelled_kwarg_raises_type_error(self) -> None:
        """Test that a misspelled parameter (e.g. `temperatur`) is rejected."""
        with pytest.raises(TypeError, match="temperatur"):

            @llm.call("openai/gpt-4o-mini", temperatur=0.7)  # type: ignore[call-arg]
            def my_call(question: str) -> str:
                return question

    def test_all_valid_params_accepted(self) -> None:
        """Test that every parameter in `llm.Params` is accepted."""

        @llm.call(
            "openai/gpt-4o-mini",
            temperature=0.7,
            max_tokens=100,
            top_p=0.9,
            top_k=40,
            seed=42,
            stop_sequences=["stop"],
            thinking={"level": "none"},
        )
        def my_call(question: str) -> str:
            return question

        assert isinstance(my_call, llm.Call)
