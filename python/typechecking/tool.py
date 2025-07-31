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


def tool_type_guards():
    @llm.tool
    def int_tool() -> int:
        return 42

    @llm.tool
    def str_tool() -> str:
        return "What is the question?"

    toolkit = llm.tools.Toolkit(tools=[int_tool, str_tool])

    tool = toolkit.get(tool_call())
    if str_tool.defines(tool):
        output: llm.ToolOutput[str] = tool.execute(tool_call())  # noqa: F841


async def async_tool_type_guards():
    @llm.tool
    async def int_tool() -> int:
        return 42

    @llm.tool
    async def str_tool() -> str:
        return "What is the question?"

    toolkit = llm.tools.Toolkit(tools=[int_tool, str_tool])

    tool = toolkit.get(tool_call())
    if str_tool.defines(tool):
        output: llm.ToolOutput[str] = await tool.execute(tool_call())  # noqa: F841
