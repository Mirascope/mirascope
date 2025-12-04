"""Simple smoke tests for the prompt decorator."""

import pytest

from mirascope import llm


class TestPromptDecoratorSmokeTests:
    """Smoke tests for each prompt type.

    This just checks that we're returning the correct Prompt type as a general
    smoke test. We don't need to unit test tools, format, etc, because the e2e
    tests make extensive use of the `llm.prompt` decorator (via `llm.call`),
    so we get full coverage of the relevant code.
    """

    def test_decorator_construction(self) -> None:
        decorator: llm.PromptDecorator[llm.Tool, None] = llm.prompt()
        assert isinstance(decorator, llm.PromptDecorator)

    def test_sync_prompt_creation(self) -> None:
        """Test that a sync function creates a Prompt."""

        @llm.prompt
        def my_prompt(question: str) -> str:
            return f"Answer this: {question}"

        assert isinstance(my_prompt, llm.Prompt)

    @pytest.mark.asyncio
    async def test_async_prompt_creation(self) -> None:
        """Test that an async function creates an AsyncPrompt."""

        @llm.prompt
        async def my_async_prompt(question: str) -> str:
            return f"Answer this: {question}"

        assert isinstance(my_async_prompt, llm.AsyncPrompt)

    def test_context_prompt_creation(self) -> None:
        """Test that a sync function with ctx parameter creates a ContextPrompt."""

        @llm.prompt
        def my_context_prompt(ctx: llm.Context[str], question: str) -> str:
            return f"Context: {ctx.deps}. Question: {question}"

        assert isinstance(my_context_prompt, llm.ContextPrompt)

    @pytest.mark.asyncio
    async def test_async_context_prompt_creation(self) -> None:
        """Test that an async function with ctx parameter creates an AsyncContextPrompt."""

        @llm.prompt
        async def my_async_context_prompt(ctx: llm.Context[str], question: str) -> str:
            return f"Context: {ctx.deps}. Question: {question}"

        assert isinstance(my_async_context_prompt, llm.AsyncContextPrompt)
