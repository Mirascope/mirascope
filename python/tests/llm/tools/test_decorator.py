"""Tests for the @tool decorator."""

from typing import Annotated

import pytest
from pydantic import Field

from mirascope import llm


class TestTool:
    """Tests for regular tool decorator (no context dependency)."""

    def test_sync_tool_basic(self) -> None:
        @llm.tool
        def add_numbers(a: int, b: int) -> int:
            """Add two numbers together."""
            return a + b

        assert isinstance(add_numbers, llm.Tool)
        assert add_numbers.name == "add_numbers"
        assert add_numbers.description == "Add two numbers together."
        assert add_numbers.strict is False

        params = add_numbers.parameters
        assert "a" in params.properties
        assert "b" in params.properties
        assert params.required == ["a", "b"]

        assert add_numbers(2, 3) == 5

        tool_call = llm.ToolCall(
            id="call_123", name="add_numbers", args='{"a": 5, "b": 7}'
        )
        output = add_numbers.execute(tool_call)
        expected = llm.ToolOutput(id="call_123", value=12, name="add_numbers")
        assert output == expected

    def test_sync_tool_with_strict(self) -> None:
        @llm.tool(strict=True)
        def multiply(x: int, y: int = 2) -> int:
            """Multiply two numbers."""
            return x * y

        assert isinstance(multiply, llm.Tool)
        assert multiply.strict is True
        assert multiply.name == "multiply"

    def test_sync_tool_with_annotated_descriptions(self) -> None:
        @llm.tool
        def get_weather(
            location: Annotated[str, Field(description="The city and state")],
            unit: Annotated[str, Field(description="Temperature unit")] = "fahrenheit",
        ) -> str:
            """Get weather for a location."""
            return f"Weather in {location} is sunny, 75°{unit[0].upper()}"

        assert isinstance(get_weather, llm.Tool)

        params = get_weather.parameters
        assert params.properties["location"]["description"] == "The city and state"
        assert params.properties["unit"]["description"] == "Temperature unit"

        result = get_weather("San Francisco, CA", "celsius")
        assert "San Francisco" in result and "75°C" in result

    @pytest.mark.asyncio
    async def test_async_tool_basic(self) -> None:
        @llm.tool
        async def async_add(a: int, b: int) -> int:
            """Add two numbers asynchronously."""
            return a + b

        assert isinstance(async_add, llm.AsyncTool)
        assert async_add.name == "async_add"
        assert async_add.description == "Add two numbers asynchronously."

        assert await async_add(3, 4) == 7

        tool_call = llm.ToolCall(
            id="call_456", name="async_add", args='{"a": 10, "b": 15}'
        )
        output = await async_add.execute(tool_call)
        expected = llm.ToolOutput(id="call_456", value=25, name="async_add")
        assert output == expected

    def test_decorator_syntax(self) -> None:
        @llm.tool
        def without_parens() -> str:
            """A simple tool."""
            return "simple"

        @llm.tool()
        def with_parens() -> str:
            """Another simple tool."""
            return "another"

        assert isinstance(without_parens, llm.Tool)
        assert without_parens.name == "without_parens"
        assert without_parens() == "simple"

        assert isinstance(with_parens, llm.Tool)
        assert with_parens.name == "with_parens"
        assert with_parens() == "another"

    def test_decorator_modes_equivalence(self) -> None:
        """Test that @tool and tool()(fn) produce equivalent results."""

        def base_func(x: int, y: str = "default") -> str:
            """A function to be decorated."""
            return f"{y}: {x}"

        decorated = llm.tool(base_func)
        via_factory = llm.tool()(base_func)

        assert decorated == via_factory

    def test_decorator_modes_equivalence_async(self) -> None:
        """Test that @tool and tool()(fn) produce equivalent results."""

        async def base_func(x: int, y: str = "default") -> str:
            """A function to be decorated."""
            return f"{y}: {x}"

        decorated = llm.tool(base_func)
        via_factory = llm.tool()(base_func)

        assert decorated == via_factory


class TestContextTool:
    """Tests for context tool decorator (with context dependency)."""

    def test_sync_context_tool_basic(self) -> None:
        @llm.tool
        def add_with_constant(ctx: llm.Context[int], a: int) -> int:
            """Add number to constant from context."""
            return a + ctx.deps

        assert isinstance(add_with_constant, llm.ContextTool)
        assert add_with_constant.name == "add_with_constant"
        assert add_with_constant.description == "Add number to constant from context."
        assert add_with_constant.strict is False

        params = add_with_constant.parameters
        assert "a" in params.properties
        assert "ctx" not in params.properties
        assert params.required == ["a"]

        context = llm.Context[int](deps=10)
        assert add_with_constant(context, 5) == 15

        tool_call = llm.ToolCall(
            id="call_123", name="add_with_constant", args='{"a": 7}'
        )
        output = add_with_constant.execute(context, tool_call)
        expected = llm.ToolOutput(id="call_123", value=17, name="add_with_constant")
        assert output == expected

    def test_sync_context_tool_with_strict(self) -> None:
        @llm.tool(strict=True)
        def multiply_with_base(ctx: llm.Context[int], x: int, y: int = 2) -> int:
            """Multiply two numbers and add base from context."""
            return (x * y) + ctx.deps

        assert isinstance(multiply_with_base, llm.ContextTool)
        assert multiply_with_base.strict is True
        assert multiply_with_base.name == "multiply_with_base"

    def test_sync_context_tool_with_annotated_descriptions(self) -> None:
        @llm.tool
        def get_weather_with_api(
            ctx: llm.Context[str],
            location: Annotated[str, Field(description="The city and state")],
            unit: Annotated[str, Field(description="Temperature unit")] = "fahrenheit",
        ) -> str:
            """Get weather for a location using API key from context."""
            return f"Weather in {location} is sunny, 75°{unit[0].upper()} (API: {ctx.deps})"

        assert isinstance(get_weather_with_api, llm.ContextTool)

        params = get_weather_with_api.parameters
        assert params.properties["location"]["description"] == "The city and state"
        assert params.properties["unit"]["description"] == "Temperature unit"

        context = llm.Context[str](deps="secret-api-key")
        result = get_weather_with_api(context, "San Francisco, CA", "celsius")
        assert (
            "San Francisco" in result
            and "75°C" in result
            and "secret-api-key" in result
        )

    @pytest.mark.asyncio
    async def test_async_context_tool_basic(self) -> None:
        @llm.tool
        async def async_add_with_base(ctx: llm.Context[int], a: int) -> int:
            """Add number to base from context asynchronously."""
            return a + ctx.deps

        assert isinstance(async_add_with_base, llm.AsyncContextTool)
        assert async_add_with_base.name == "async_add_with_base"
        assert (
            async_add_with_base.description
            == "Add number to base from context asynchronously."
        )

        context = llm.Context[int](deps=15)
        assert await async_add_with_base(context, 10) == 25

        tool_call = llm.ToolCall(
            id="call_456", name="async_add_with_base", args='{"a": 20}'
        )
        output = await async_add_with_base.execute(context, tool_call)
        expected = llm.ToolOutput(id="call_456", value=35, name="async_add_with_base")
        assert output == expected

    def test_decorator_syntax(self) -> None:
        @llm.tool
        def without_parens(ctx: llm.Context[int]) -> str:
            """A simple context tool."""
            return f"simple-{ctx.deps}"

        @llm.tool()
        def with_parens(ctx: llm.Context[int]) -> str:
            """Another simple context tool."""
            return f"another-{ctx.deps}"

        assert isinstance(without_parens, llm.ContextTool)
        assert without_parens.name == "without_parens"

        context = llm.Context[int](deps=42)
        assert without_parens(context) == "simple-42"

        assert isinstance(with_parens, llm.ContextTool)
        assert with_parens.name == "with_parens"
        assert with_parens(context) == "another-42"

    def test_decorator_modes_equivalence(self) -> None:
        """Test that @context_tool and context_tool()(fn) produce equivalent results."""

        def base_func(ctx: llm.Context[int], x: int, y: str = "default") -> str:
            """A function to be decorated."""
            return f"{y}: {x + ctx.deps}"

        decorated = llm.tool(base_func)
        via_factory = llm.tool()(base_func)

        assert decorated == via_factory

    def test_decorator_modes_equivalence_async(self) -> None:
        """Test that @context_tool and context_tool()(fn) produce equivalent results for async."""

        async def base_func(ctx: llm.Context[int], x: int, y: str = "default") -> str:
            """A function to be decorated."""
            return f"{y}: {x + ctx.deps}"

        decorated = llm.tool(base_func)
        via_factory = llm.tool()(base_func)

        assert decorated == via_factory

    def test_parameter_filtering(self) -> None:
        """Test that context parameter is filtered out of tool schema."""

        @llm.tool
        def test_func(
            ctx: llm.Context[str], param1: int, param2: str = "default"
        ) -> str:
            """Test function with context and regular parameters."""
            return f"{param2}-{param1}-{ctx.deps}"

        params = test_func.parameters

        assert set(params.properties.keys()) == {"param1", "param2"}
        assert "ctx" not in params.properties
        assert params.required == ["param1"]

    def test_context_parameter_name_must_be_ctx(self) -> None:
        """Test that context tools work require the first parameter be named `ctx`."""

        @llm.tool
        def context_weird_name(special_context: llm.Context[str], value: int) -> str:
            return f"{special_context.deps}-{value}"

        assert isinstance(context_weird_name, llm.Tool)
        assert "special_context" in context_weird_name.parameters.properties
        assert "value" in context_weird_name.parameters.properties

    def test_async_context_parameter_name_must_be_ctx(self) -> None:
        """Test that async context tools work require the first parameter be named `ctx`."""

        @llm.tool
        async def context_weird_name(
            special_context: llm.Context[str], value: int
        ) -> str:
            return f"{special_context.deps}-{value}"

        assert isinstance(context_weird_name, llm.AsyncTool)
        assert "special_context" in context_weird_name.parameters.properties
        assert "value" in context_weird_name.parameters.properties

    def test_untyped_parameter(self) -> None:
        """Test that untyped ctx parameters don't become context tools."""

        @llm.tool
        def non_context_tool(ctx) -> str:  # pyright: ignore[reportMissingParameterType]  # noqa: ANN001
            return f"{ctx}"

        assert isinstance(non_context_tool, llm.Tool)
        assert "ctx" in non_context_tool.parameters.properties

    def test_async_untyped_parameter(self) -> None:
        """Test that untyped ctx parameters don't become context tools."""

        @llm.tool
        async def non_context_tool(ctx) -> str:  # pyright: ignore[reportMissingParameterType]  # noqa: ANN001
            return f"{ctx}"

        assert isinstance(non_context_tool, llm.AsyncTool)
        assert "ctx" in non_context_tool.parameters.properties

    def test_non_context_typed_parameter(self) -> None:
        """Test that non-Context typed parameters are not treated as context tools."""

        @llm.tool
        def non_context_tool(ctx: int) -> str:
            return f"{ctx}"

        assert isinstance(non_context_tool, llm.Tool)
        assert "ctx" in non_context_tool.parameters.properties

    def test_async_non_context_typed_parameter(self) -> None:
        """Test that non-Context typed async parameters are not treated as context tools."""

        @llm.tool
        async def non_context_tool(ctx: int) -> str:
            return f"{ctx}"

        assert isinstance(non_context_tool, llm.AsyncTool)
        assert "ctx" in non_context_tool.parameters.properties

    def test_method_with_context_after_self(self) -> None:
        """Test that methods with self as first arg and Context as second arg are context tools."""

        class TestClass:
            @llm.tool
            def method_with_context(self, ctx: llm.Context[str], value: int) -> str:
                return f"{ctx.deps}-{value}"

        assert isinstance(TestClass.method_with_context, llm.ContextTool)
        assert "ctx" not in TestClass.method_with_context.parameters.properties
        assert "value" in TestClass.method_with_context.parameters.properties

    def test_async_method_with_context_after_self(self) -> None:
        """Test that async methods with self as first arg and Context as second arg are context tools."""

        class TestClass:
            @llm.tool
            async def method_with_context(
                self, ctx: llm.Context[str], value: int
            ) -> str:
                return f"{ctx.deps}-{value}"

        assert isinstance(TestClass.method_with_context, llm.AsyncContextTool)
        assert "ctx" not in TestClass.method_with_context.parameters.properties
        assert "value" in TestClass.method_with_context.parameters.properties

    def test_context_not_first_parameter(self) -> None:
        """Test that Context as second parameter (after non-self) is not treated as context tool."""

        @llm.tool
        def second_arg_context(regular_param: int, ctx: llm.Context[str]) -> str:
            return f"{regular_param}-{ctx.deps}"

        assert isinstance(second_arg_context, llm.Tool)
        assert "regular_param" in second_arg_context.parameters.properties
        assert "ctx" in second_arg_context.parameters.properties

    def test_async_context_not_first_parameter(self) -> None:
        """Test that Context as second parameter (after non-self) is not treated as async context tool."""

        @llm.tool
        async def second_arg_context(regular_param: int, ctx: llm.Context[str]) -> str:
            return f"{regular_param}-{ctx.deps}"

        assert isinstance(second_arg_context, llm.AsyncTool)
        assert "regular_param" in second_arg_context.parameters.properties
        assert "ctx" in second_arg_context.parameters.properties

    def test_context_subclass_detection(self) -> None:
        """Test that Context subclasses are properly detected as context tools."""

        class CustomContext(llm.Context[str]): ...

        @llm.tool
        def with_custom_context(ctx: CustomContext, value: int) -> str:
            return str(value)

        assert isinstance(with_custom_context, llm.ContextTool)
        assert "ctx" not in with_custom_context.parameters.properties
        assert "value" in with_custom_context.parameters.properties

    def test_async_context_subclass_detection(self) -> None:
        """Test that Context subclasses are properly detected as async context tools."""

        class CustomContext(llm.Context[str]): ...

        @llm.tool
        async def with_custom_context(ctx: CustomContext, value: int) -> str:
            return str(value)

        assert isinstance(with_custom_context, llm.AsyncContextTool)
        assert "ctx" not in with_custom_context.parameters.properties
        assert "value" in with_custom_context.parameters.properties
