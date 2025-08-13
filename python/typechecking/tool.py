"""Type safety testing for tools"""

from mirascope import llm

from .utils import (
    async_tool,
    tool,
    tool_call,
)


async def tool_call_patterns():
    x1: llm.ToolOutput[int] = tool.execute(tool_call())  # noqa: F841
    y1: int = tool()  # noqa: F841

    x2: llm.ToolOutput[int] = await async_tool.execute(tool_call())  # noqa: F841
    y2: int = await async_tool()  # noqa: F841
