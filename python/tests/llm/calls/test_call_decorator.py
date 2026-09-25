"""Simple smoke tests for the call decorator."""

from collections.abc import Callable
from typing import cast

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

    @pytest.mark.parametrize(
        "unknown_param", ["nonsense_kwarg", "temperatur", "provider"]
    )
    def test_unknown_params_are_rejected(self, unknown_param: str) -> None:
        """Reject misspelled and removed call parameters at decoration time."""
        call = cast(Callable[..., object], llm.call)
        with pytest.raises(
            TypeError,
            match=rf"llm\.call\(\) got unexpected keyword argument.*'{unknown_param}'",
        ):
            call("openai/gpt-4o-mini", **{unknown_param: 123})

    def test_removed_provider_param_explains_migration(self) -> None:
        """Explain provider selection even with an old, unprefixed model ID."""
        call = cast(Callable[..., object], llm.call)
        with pytest.raises(
            TypeError, match="Provider selection is part of the model ID"
        ):
            call("gpt-4o-mini", provider="openai")

    def test_multiple_unknown_params_are_reported(self) -> None:
        """Report all invalid keys so users can fix them together."""
        call = cast(Callable[..., object], llm.call)
        with pytest.raises(
            TypeError,
            match="unexpected keyword arguments: 'nonsense_kwarg', 'temperatur'",
        ):
            call("openai/gpt-4o-mini", temperatur=0.7, nonsense_kwarg=123)

    def test_known_params_are_preserved(self) -> None:
        """Keep supported model parameters on the decorated call."""
        decorated = llm.call("openai/gpt-4o-mini", temperature=0.7)

        assert decorated.model.params == {"temperature": 0.7}

    def test_model_instance_is_preserved(self) -> None:
        """Keep accepting an existing model with its configured parameters."""
        model = llm.Model("openai/gpt-4o-mini", temperature=0.7)

        assert llm.call(model).model is model
