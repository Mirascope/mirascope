"""Type safety testing for context tools"""

from mirascope import llm

from .utils import (
    async_context_tool,
    context_tool,
    tool_call,
)


def deps_mismatch_failures():
    def no_context() -> int:
        return 42

    def async_no_context() -> int:
        return 42

    llm.context_tool(no_context)  # type: ignore[reportCallIssue]
    llm.context_tool(async_no_context)  # type: ignore[reportCallIssue]


async def tool_call_patterns():
    ctx = llm.Context()
    x1: llm.ToolOutput[int] = context_tool.execute(ctx, tool_call())  # noqa: F841
    y1: int = context_tool(ctx)  # noqa: F841

    x2: llm.ToolOutput[int] = await async_context_tool.execute(ctx, tool_call())  # noqa: F841
    y2: int = await async_context_tool(ctx)  # noqa: F841
