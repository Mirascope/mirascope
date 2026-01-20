"""Tests for toolkit classes."""

from typing import Any

import pytest

from mirascope import llm


@pytest.fixture
def tool_call() -> llm.ToolCall:
    """Create a mock tool call for testing."""
    return llm.ToolCall(name="test_tool", id="abc", args='{"arg": "value"}')


@pytest.fixture
def tools() -> list[llm.Tool]:
    """Create mock tools for testing."""

    @llm.tool
    def test_tool(arg: str) -> str:
        return f"result: {arg}"

    @llm.tool
    def other_tool() -> int:
        return 42

    return [test_tool, other_tool]


@pytest.fixture
def async_tools() -> list[llm.AsyncTool]:
    """Create mock async tools for testing."""

    @llm.tool
    async def test_tool(arg: str) -> str:
        return f"result: {arg}"

    @llm.tool
    async def other_tool() -> int:
        return 42

    return [test_tool, other_tool]


def test_toolkit_init_success(tools: list[llm.Tool]) -> None:
    """Test that Toolkit initializes successfully with unique tool names."""
    toolkit = llm.Toolkit(tools=tools)
    assert toolkit.tools == tools


def test_toolkit_init_duplicate_names() -> None:
    """Test that Toolkit raises ValueError for duplicate tool names."""

    def create_tool() -> llm.Tool:
        @llm.tool
        def tool() -> int:
            return 42

        return tool

    with pytest.raises(ValueError, match="Multiple tools with name: tool"):
        llm.Toolkit(tools=[create_tool(), create_tool()])


def test_toolkit_get_existing_tool(
    tools: list[llm.Tool], tool_call: llm.ToolCall
) -> None:
    """Test that get returns the correct tool for an existing tool name."""
    toolkit = llm.Toolkit(tools=tools)
    tool = toolkit.get(tool_call)
    assert tool.name == "test_tool"


def test_toolkit_get_nonexistent_tool(tool_call: llm.ToolCall) -> None:
    """Test that get raises ToolNotFoundError for nonexistent tool."""
    toolkit = llm.Toolkit(tools=[])

    with pytest.raises(
        llm.ToolNotFoundError,
        match=f"Tool '{tool_call.name}' not found in registered tools",
    ):
        toolkit.get(tool_call)


def test_toolkit_execute_nonexistent_tool(tool_call: llm.ToolCall) -> None:
    """Test that execute returns ToolOutput with error for nonexistent tool."""
    toolkit = llm.Toolkit(tools=[])

    output = toolkit.execute(tool_call)
    assert output.error is not None
    assert isinstance(output.error, llm.ToolNotFoundError)
    assert output.result == f"Tool '{tool_call.name}' not found in registered tools"


def test_toolkit_execute(tools: list[llm.Tool], tool_call: llm.ToolCall) -> None:
    """Test that execute runs the correct tool and returns output."""
    toolkit = llm.Toolkit(tools=tools)
    output = toolkit.execute(tool_call)

    assert output.result == "result: value"


@pytest.mark.asyncio
async def test_async_toolkit_init_success(async_tools: list[llm.AsyncTool]) -> None:
    """Test that AsyncToolkit initializes successfully with unique tool names."""
    toolkit = llm.AsyncToolkit(tools=async_tools)
    assert toolkit.tools == async_tools


@pytest.mark.asyncio
async def test_async_toolkit_get_existing_tool(
    async_tools: list[llm.AsyncTool], tool_call: llm.ToolCall
) -> None:
    """Test that get returns the correct tool for an existing tool name."""
    toolkit = llm.AsyncToolkit(tools=async_tools)
    tool = toolkit.get(tool_call)
    assert tool.name == "test_tool"


@pytest.mark.asyncio
async def test_async_toolkit_get_nonexistent_tool(tool_call: llm.ToolCall) -> None:
    """Test that get raises ToolNotFoundError for missing tool."""
    toolkit = llm.AsyncToolkit(tools=[])

    with pytest.raises(
        llm.ToolNotFoundError,
        match=f"Tool '{tool_call.name}' not found in registered tools",
    ):
        toolkit.get(tool_call)


@pytest.mark.asyncio
async def test_async_toolkit_execute_nonexistent_tool(tool_call: llm.ToolCall) -> None:
    """Test that execute returns ToolOutput with error for nonexistent tool."""
    toolkit = llm.AsyncToolkit(tools=[])

    output = await toolkit.execute(tool_call)
    assert output.error is not None
    assert isinstance(output.error, llm.ToolNotFoundError)
    assert output.result == f"Tool '{tool_call.name}' not found in registered tools"


@pytest.mark.asyncio
async def test_async_toolkit_execute(
    async_tools: list[llm.AsyncTool], tool_call: llm.ToolCall
) -> None:
    """Test that execute runs the correct tool and returns output."""
    toolkit = llm.AsyncToolkit(tools=async_tools)
    output = await toolkit.execute(tool_call)

    assert output.result == "result: value"


@pytest.fixture
def context_tool_call() -> llm.ToolCall:
    """Create a mock tool call for testing."""
    return llm.ToolCall(name="deps_tool", id="bef", args="{}")


@pytest.fixture
def context_tool() -> llm.ContextTool[Any]:
    """Create mock context tool for testing."""

    @llm.tool
    def deps_tool(ctx: llm.Context[Any]) -> str:
        return f"deps: {ctx.deps}"

    return deps_tool


@pytest.fixture
def async_context_tool() -> llm.AsyncContextTool[Any]:
    """Create mock context tool for testing."""

    @llm.tool
    async def deps_tool(ctx: llm.Context[Any]) -> str:
        return f"deps: {ctx.deps}"

    return deps_tool


def test_context_toolkit_execute(
    tools: list[llm.Tool],
    context_tool: llm.ContextTool[Any],
    tool_call: llm.ToolCall,
    context_tool_call: llm.ToolCall,
) -> None:
    """Test that execute runs the correct tool and returns output, including context tools."""
    toolkit = llm.ContextToolkit(tools=[*tools, context_tool])
    ctx = llm.Context(deps=None)

    output = toolkit.execute(ctx, tool_call)
    assert output.result == "result: value"

    output = toolkit.execute(ctx, context_tool_call)
    assert output.result == "deps: None"


def test_context_toolkit_execute_nonexistent_tool(tool_call: llm.ToolCall) -> None:
    """Test that execute returns ToolOutput with error for nonexistent tool."""
    toolkit = llm.ContextToolkit[None](tools=[])
    ctx = llm.Context(deps=None)

    output = toolkit.execute(ctx, tool_call)
    assert output.error is not None
    assert isinstance(output.error, llm.ToolNotFoundError)
    assert output.result == f"Tool '{tool_call.name}' not found in registered tools"


@pytest.mark.asyncio
async def test_async_context_toolkit_execute(
    async_tools: list[llm.AsyncTool],
    async_context_tool: llm.AsyncContextTool[Any],
    tool_call: llm.ToolCall,
    context_tool_call: llm.ToolCall,
) -> None:
    """Test that execute runs the correct tool and returns output, including context tools."""
    toolkit = llm.AsyncContextToolkit(tools=[*async_tools, async_context_tool])
    ctx = llm.Context(deps=None)

    output = await toolkit.execute(ctx, tool_call)
    assert output.result == "result: value"

    output = await toolkit.execute(ctx, context_tool_call)
    assert output.result == "deps: None"


@pytest.mark.asyncio
async def test_async_context_toolkit_execute_nonexistent_tool(
    tool_call: llm.ToolCall,
) -> None:
    """Test that execute returns ToolOutput with error for nonexistent tool."""
    toolkit = llm.AsyncContextToolkit[None](tools=[])
    ctx = llm.Context(deps=None)

    output = await toolkit.execute(ctx, tool_call)
    assert output.error is not None
    assert isinstance(output.error, llm.ToolNotFoundError)
    assert output.result == f"Tool '{tool_call.name}' not found in registered tools"
