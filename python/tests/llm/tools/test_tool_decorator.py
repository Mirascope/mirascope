"""Tests for the @tool decorator."""

from typing import Annotated

import pytest
from pydantic import Field

from mirascope import llm


def test_sync_tool_basic() -> None:
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

    tool_call = llm.ToolCall(id="call_123", name="add_numbers", args='{"a": 5, "b": 7}')
    output = add_numbers.execute(tool_call)
    expected = llm.ToolOutput(id="call_123", value=12, name="add_numbers")
    assert output == expected


def test_sync_tool_with_strict() -> None:
    @llm.tool(strict=True)
    def multiply(x: int, y: int = 2) -> int:
        """Multiply two numbers."""
        return x * y

    assert isinstance(multiply, llm.Tool)
    assert multiply.strict is True
    assert multiply.name == "multiply"


def test_sync_tool_with_annotated_descriptions() -> None:
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
async def test_async_tool_basic() -> None:
    @llm.tool
    async def async_add(a: int, b: int) -> int:
        """Add two numbers asynchronously."""
        return a + b

    assert isinstance(async_add, llm.AsyncTool)
    assert async_add.name == "async_add"
    assert async_add.description == "Add two numbers asynchronously."

    assert await async_add(3, 4) == 7

    tool_call = llm.ToolCall(id="call_456", name="async_add", args='{"a": 10, "b": 15}')
    output = await async_add.execute(tool_call)
    expected = llm.ToolOutput(id="call_456", value=25, name="async_add")
    assert output == expected


def test_tool_decorator_syntax() -> None:
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


def test_decorator_modes_equivalence() -> None:
    """Test that @tool and tool()(fn) produce equivalent results."""

    def base_func(x: int, y: str = "default") -> str:
        """A function to be decorated."""
        return f"{y}: {x}"

    decorated = llm.tool(base_func)
    via_factory = llm.tool()(base_func)

    # Should be equal llm.Tool instances
    assert decorated == via_factory


def test_decorator_modes_equivalence_async() -> None:
    """Test that @tool and tool()(fn) produce equivalent results."""

    async def base_func(x: int, y: str = "default") -> str:
        """A function to be decorated."""
        return f"{y}: {x}"

    decorated = llm.tool(base_func)
    via_factory = llm.tool()(base_func)

    # Should be equal llm.Tool instances
    assert decorated == via_factory
