"""Type safety testing for tools"""

from mirascope import llm

from .utils import (
    async_context_tool,
    async_tool,
    context,
    context_tool,
    tool,
    tool_call,
)


async def tool_call_patterns():
    x1: llm.ToolOutput[int] = tool.execute(tool_call())  # noqa: F841
    y1: int = tool()  # noqa: F841

    x2: llm.ToolOutput[int] = await async_tool.execute(tool_call())  # noqa: F841
    y2: int = await async_tool()  # noqa: F841


async def context_tool_call_patterns():
    ctx = context()
    x1: llm.ToolOutput[int] = context_tool.execute(ctx, tool_call())  # noqa: F841
    y1: int = context_tool(ctx)  # noqa: F841

    x2: llm.ToolOutput[int] = await async_context_tool.execute(ctx, tool_call())  # noqa: F841
    y2: int = await async_context_tool(ctx)  # noqa: F841


def context_tool_deps():
    @llm.tool
    def ctx_tool(ctx: llm.Context[int]) -> str:
        return str(ctx.deps)

    x: llm.ContextTool[int] = ctx_tool  # noqa: F841
    # Following line must type error, shows that we infer the deps type correctly
    y: llm.ContextTool[str] = ctx_tool  # pyright: ignore[reportAssignmentType]  # noqa: F841
