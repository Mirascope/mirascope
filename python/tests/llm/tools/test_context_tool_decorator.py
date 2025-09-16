"""Tests for the @context_tool decorator."""

from typing import Annotated

import pytest
from pydantic import Field

from mirascope import llm


def test_sync_context_tool_basic() -> None:
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

    tool_call = llm.ToolCall(id="call_123", name="add_with_constant", args='{"a": 7}')
    output = add_with_constant.execute(context, tool_call)
    expected = llm.ToolOutput(id="call_123", value=17, name="add_with_constant")
    assert output == expected


def test_sync_context_tool_with_strict() -> None:
    @llm.tool(strict=True)
    def multiply_with_base(ctx: llm.Context[int], x: int, y: int = 2) -> int:
        """Multiply two numbers and add base from context."""
        return (x * y) + ctx.deps

    assert isinstance(multiply_with_base, llm.ContextTool)
    assert multiply_with_base.strict is True
    assert multiply_with_base.name == "multiply_with_base"


def test_sync_context_tool_with_annotated_descriptions() -> None:
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
    assert "San Francisco" in result and "75°C" in result and "secret-api-key" in result


@pytest.mark.asyncio
async def test_async_context_tool_basic() -> None:
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


def test_context_tool_decorator_syntax() -> None:
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


def test_context_tool_decorator_modes_equivalence() -> None:
    """Test that @context_tool and context_tool()(fn) produce equivalent results."""

    def base_func(ctx: llm.Context[int], x: int, y: str = "default") -> str:
        """A function to be decorated."""
        return f"{y}: {x + ctx.deps}"

    decorated = llm.tool(base_func)
    via_factory = llm.tool()(base_func)

    assert decorated == via_factory


def test_context_tool_decorator_modes_equivalence_async() -> None:
    """Test that @context_tool and context_tool()(fn) produce equivalent results for async."""

    async def base_func(ctx: llm.Context[int], x: int, y: str = "default") -> str:
        """A function to be decorated."""
        return f"{y}: {x + ctx.deps}"

    decorated = llm.tool(base_func)
    via_factory = llm.tool()(base_func)

    assert decorated == via_factory


def test_context_tool_parameter_filtering() -> None:
    """Test that context parameter is filtered out of tool schema."""

    @llm.tool
    def test_func(ctx: llm.Context[str], param1: int, param2: str = "default") -> str:
        """Test function with context and regular parameters."""
        return f"{param2}-{param1}-{ctx.deps}"

    params = test_func.parameters

    assert set(params.properties.keys()) == {"param1", "param2"}
    assert "ctx" not in params.properties
    assert params.required == ["param1"]
