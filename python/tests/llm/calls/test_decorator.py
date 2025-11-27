"""Tests for the call decorator function."""

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
def context_tools() -> list[llm.ContextTool[int]]:
    """Create a mock context tool for testing."""

    @llm.tool
    def context_tool(ctx: llm.Context[int]) -> int:
        return ctx.deps

    return [context_tool]


@pytest.fixture
def async_tools() -> list[llm.AsyncTool]:
    """Create a mock tool for testing."""

    @llm.tool
    async def tool() -> int:
        return 42

    return [tool]


@pytest.fixture
def async_context_tools() -> list[llm.AsyncContextTool[int]]:
    """Create a mock async context tool for testing."""

    @llm.tool
    async def async_context_tool(ctx: llm.Context[int]) -> int:
        return ctx.deps

    return [async_context_tool]


@pytest.fixture
def params() -> llm.clients.Params:
    return {"temperature": 0.7, "max_tokens": 100}


class TestCall:
    """Tests for regular call decorator (no context dependency)."""

    def test_call_decorator_creation_openai(
        self, tools: list[llm.Tool], params: llm.clients.Params
    ) -> None:
        """Test that call decorator creates CallDecorator with correct parameters for OpenAI."""

        decorator = llm.call(
            provider="openai:completions",
            model_id="openai/gpt-5-mini",
            tools=tools,
            format=Format,
            **params,
        )

        assert decorator.tools is tools
        assert decorator.format is Format
        assert decorator.model.provider == "openai:completions"
        assert decorator.model.model_id == "openai/gpt-5-mini"
        assert decorator.model.params == params

    def test_creating_sync_call(
        self, tools: list[llm.Tool], params: llm.clients.Params
    ) -> None:
        """Test that call decorator creates CallDecorator with correct parameters for OpenAI."""

        def prompt() -> str:
            return "Please recommend a fantasy book."

        call = llm.call(
            provider="openai:completions",
            model_id="openai/gpt-5-mini",
            tools=tools,
            format=Format,
            **params,
        )(prompt)

        assert isinstance(call, llm.calls.Call)

        assert call.model.provider == "openai:completions"
        assert call.model.model_id == "openai/gpt-5-mini"
        assert call.model.params == params

        assert call.toolkit == llm.Toolkit(tools=tools)
        assert call.format is Format
        assert call.fn() == [llm.messages.user("Please recommend a fantasy book.")]

    @pytest.mark.asyncio
    async def test_creating_async_call(
        self, async_tools: list[llm.AsyncTool], params: llm.clients.Params
    ) -> None:
        """Test that call decorator creates CallDecorator with correct parameters for OpenAI."""

        async def async_prompt() -> str:
            return "Please recommend a fantasy book."

        call = llm.call(
            provider="openai:completions",
            model_id="openai/gpt-5-mini",
            tools=async_tools,
            format=Format,
            **params,
        )(async_prompt)

        assert isinstance(call, llm.calls.AsyncCall)

        assert call.model.provider == "openai:completions"
        assert call.model.model_id == "openai/gpt-5-mini"
        assert call.model.params == params

        assert call.toolkit == llm.AsyncToolkit(tools=async_tools)
        assert call.format is Format
        assert await call.fn() == [
            llm.messages.user("Please recommend a fantasy book.")
        ]

    @pytest.mark.vcr()
    def test_call_decorator_e2e_model_override(self) -> None:
        # TODO: Remove e2e tests from non-e2e test directory; either add model
        # override test coverage to e2e, or refactor this to use mocking etc.
        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        def call() -> str:
            return "What company created you? Answer in just one word."

        assert call().pretty() == snapshot("OpenAI.")
        with llm.model(provider="google", model_id="google/gemini-2.0-flash"):
            assert call().pretty() == snapshot("Google.\n")
            with llm.model(
                provider="anthropic", model_id="anthropic/claude-sonnet-4-0"
            ):
                assert call().pretty() == snapshot("Anthropic")

    def test_value_error_invalid_provider(self) -> None:
        with pytest.raises(ValueError, match="Unknown provider: nonexistent"):
            llm.call(provider="nonexistent", model_id="openai/gpt-5-mini")  # pyright: ignore[reportCallIssue, reportArgumentType]


class TestContextCall:
    """Tests for context call decorator (with context dependency)."""

    def test_context_call_decorator_creation_openai(
        self, context_tools: list[llm.ContextTool[int]], params: llm.clients.Params
    ) -> None:
        """Test that context_call decorator creates ContextCallDecorator with correct parameters for OpenAI."""

        decorator = llm.call(
            provider="openai:completions",
            model_id="openai/gpt-5-mini",
            tools=context_tools,
            format=Format,
            **params,
        )

        assert decorator.tools is context_tools
        assert decorator.format is Format
        assert decorator.model.provider == "openai:completions"
        assert decorator.model.model_id == "openai/gpt-5-mini"
        assert decorator.model.params == params

    def test_creating_sync_context_call(
        self, context_tools: list[llm.ContextTool[int]], params: llm.clients.Params
    ) -> None:
        """Test that context_call decorator creates ContextCall with correct parameters."""

        def context_prompt(ctx: llm.Context[int]) -> str:
            return f"Please recommend a fantasy book. My context value is {ctx.deps}."

        call = llm.call(
            provider="openai:completions",
            model_id="openai/gpt-5-mini",
            tools=context_tools,
            format=Format,
            **params,
        )(context_prompt)

        assert isinstance(call, llm.calls.ContextCall)

        assert call.model.provider == "openai:completions"
        assert call.model.model_id == "openai/gpt-5-mini"
        assert call.model.params == params

        assert call.toolkit == llm.ContextToolkit(tools=context_tools)
        assert call.format is Format
        ctx = llm.Context(deps=42)
        assert call.fn(ctx) == [
            llm.messages.user(
                "Please recommend a fantasy book. My context value is 42."
            )
        ]

    @pytest.mark.asyncio
    async def test_creating_async_context_call(
        self,
        async_context_tools: list[llm.AsyncContextTool[int]],
        params: llm.clients.Params,
    ) -> None:
        """Test that context_call decorator creates AsyncContextCall with correct parameters."""

        async def async_context_prompt(ctx: llm.Context[int]) -> str:
            return f"Please recommend a fantasy book. My context value is {ctx.deps}."

        call = llm.call(
            provider="openai:completions",
            model_id="openai/gpt-5-mini",
            tools=async_context_tools,
            format=Format,
            **params,
        )(async_context_prompt)

        assert isinstance(call, llm.calls.AsyncContextCall)

        assert call.model.provider == "openai:completions"
        assert call.model.model_id == "openai/gpt-5-mini"
        assert call.model.params == params

        assert call.toolkit == llm.AsyncContextToolkit(tools=async_context_tools)
        assert call.format is Format
        ctx = llm.Context(deps=42)
        assert await call.fn(ctx) == [
            llm.messages.user(
                "Please recommend a fantasy book. My context value is 42."
            )
        ]

    def test_context_call_decorator_with_mixed_tools(
        self, tools: list[llm.Tool], params: llm.clients.Params
    ) -> None:
        """Test that context_call decorator works with regular tools too."""

        def context_prompt(ctx: llm.Context[int]) -> str:
            return f"Please recommend a fantasy book. My context value is {ctx.deps}."

        call = llm.call(
            provider="openai:completions",
            model_id="openai/gpt-5-mini",
            tools=tools,
            format=Format,
            **params,
        )(context_prompt)

        assert isinstance(call, llm.calls.ContextCall)
        assert call.toolkit == llm.ContextToolkit(tools=tools)

    @pytest.mark.vcr()
    def test_context_call_decorator_e2e_model_override(self) -> None:
        # TODO: Remove e2e tests from non-e2e test directory; either add model
        # override test coverage to e2e, or refactor this to use mocking etc.
        ctx = llm.Context(deps="Who created you?")

        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        def call(ctx: llm.Context[str]) -> str:
            return f"Answer the question in just one word: {ctx.deps}."

        assert call(ctx).pretty() == snapshot("OpenAI.")
        with llm.model(provider="google", model_id="google/gemini-2.0-flash"):
            assert call(ctx).pretty() == snapshot("Google.\n")
            with llm.model(
                provider="anthropic", model_id="anthropic/claude-sonnet-4-0"
            ):
                assert call(ctx).pretty() == snapshot("Anthropic.")

    def test_context_parameter_name_independence(self) -> None:
        """Test that context prompts require the first parameter be named ctx."""

        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        def context_weird_name(special_context: llm.Context[str]) -> str:
            return f"Value: {special_context.deps}"

        assert isinstance(context_weird_name, llm.calls.Call)

    def test_async_context_parameter_name_independence(self) -> None:
        """Test that async context prompts require the first parameter be named ctx."""

        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        async def context_weird_name(special_context: llm.Context[str]) -> str:
            return f"Value: {special_context.deps}"

        assert isinstance(context_weird_name, llm.calls.AsyncCall)

    def test_non_context_typed_parameter(self) -> None:
        """Test that non-Context typed parameters are not treated as context prompts."""

        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        def non_context_prompt(ctx: int) -> str:
            return f"Value: {ctx}"

        assert isinstance(non_context_prompt, llm.calls.Call)

    def test_async_non_context_typed_parameter(self) -> None:
        """Test that non-Context typed async parameters are not treated as context prompts."""

        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        async def non_context_prompt(ctx: int) -> str:
            return f"Value: {ctx}"

        assert isinstance(non_context_prompt, llm.calls.AsyncCall)

    def test_missing_type_annotation(self) -> None:
        """Test that missing type annotations are not treated as context prompts."""

        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        def missing_annotation_prompt(ctx) -> str:  # pyright: ignore[reportMissingParameterType] # noqa: ANN001
            return "hi"

        assert isinstance(missing_annotation_prompt, llm.calls.Call)

    def test_async_missing_type_annotation(self) -> None:
        """Test that missing type annotations are not treated as async context prompts."""

        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        async def missing_annotation_prompt(ctx) -> str:  # pyright: ignore[reportMissingParameterType] # noqa: ANN001
            return "hi"

        assert isinstance(missing_annotation_prompt, llm.calls.AsyncCall)

    def test_method_with_context_after_self(self) -> None:
        """Test that methods with self as first arg and Context as second arg are context prompts."""

        class TestClass:
            @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
            def method_with_context(self, ctx: llm.Context[str]) -> str:
                return f"Value: {ctx.deps}"

        assert isinstance(TestClass.method_with_context, llm.calls.ContextCall)

    def test_async_method_with_context_after_self(self) -> None:
        """Test that async methods with self as first arg and Context as second arg are context prompts."""

        class TestClass:
            @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
            async def method_with_context(self, ctx: llm.Context[str]) -> str:
                return f"Value: {ctx.deps}"

        assert isinstance(TestClass.method_with_context, llm.calls.AsyncContextCall)

    def test_context_not_first_parameter(self) -> None:
        """Test that Context as second parameter (after non-self) is not treated as context prompt."""

        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        def second_arg_context(regular_param: int, ctx: llm.Context[str]) -> str:
            return f"Value: {regular_param}-{ctx.deps}"

        assert isinstance(second_arg_context, llm.calls.Call)

    def test_async_context_not_first_parameter(self) -> None:
        """Test that Context as second parameter (after non-self) is not treated as async context prompt."""

        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        async def second_arg_context(regular_param: int, ctx: llm.Context[str]) -> str:
            return f"Value: {regular_param}-{ctx.deps}"

        assert isinstance(second_arg_context, llm.calls.AsyncCall)

    def test_context_subclass_detection(self) -> None:
        """Test that Context subclasses are properly detected as context prompts."""

        class CustomContext(llm.Context[str]): ...

        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        def with_custom_context(ctx: CustomContext) -> str:
            return str(ctx.deps)

        assert isinstance(with_custom_context, llm.calls.ContextCall)

    def test_async_context_subclass_detection(self) -> None:
        """Test that Context subclasses are properly detected as async context prompts."""

        class CustomContext(llm.Context[str]): ...

        @llm.call(provider="openai:completions", model_id="openai/gpt-5-mini")
        async def with_custom_context(ctx: CustomContext) -> str:
            return str(ctx.deps)

        assert isinstance(with_custom_context, llm.calls.AsyncContextCall)
