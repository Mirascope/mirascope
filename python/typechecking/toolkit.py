"""Type safety testing for toolkit.get and toolkit.call"""

from collections.abc import Awaitable

from typing_extensions import assert_type

from mirascope import llm

from .utils import (
    async_context_tool,
    async_tool,
    context_tool,
    expect_async_context_tool,
    expect_async_tool,
    expect_context_tool,
    expect_tool,
    tool,
    tool_call,
)


async def regular_toolkit():
    sync_toolkit = llm.tools.Toolkit(tools=[tool])
    expect_tool(sync_toolkit.get(tool_call()))
    assert_type(sync_toolkit.call(tool_call()), llm.ToolOutput[int])

    async_toolkit = llm.tools.Toolkit(tools=[async_tool])
    expect_async_tool(async_toolkit.get(tool_call()))
    assert_type(async_toolkit.call(tool_call()), Awaitable[llm.ToolOutput[int]])

    mixed_toolkit = llm.tools.Toolkit(tools=[tool, async_tool])
    mixed_tool: llm.tools.Tool | llm.tools.AsyncTool = mixed_toolkit.get(tool_call())  # noqa: F841
    output: llm.ToolOutput | Awaitable[llm.ToolOutput] = mixed_toolkit.call(tool_call())  # noqa: F841


async def context_toolkit_non_context_tools():
    empty_ctx = llm.Context()
    sync_toolkit = llm.tools.ContextToolkit(tools=[tool])
    expect_tool(sync_toolkit.get(empty_ctx, tool_call()))
    assert_type(sync_toolkit.call(empty_ctx, tool_call()), llm.ToolOutput[int])

    async_toolkit = llm.tools.ContextToolkit(tools=[async_tool])
    expect_async_tool(async_toolkit.get(empty_ctx, tool_call()))
    assert_type(
        async_toolkit.call(empty_ctx, tool_call()), Awaitable[llm.ToolOutput[int]]
    )

    mixed_toolkit = llm.tools.ContextToolkit(tools=[tool, async_tool])
    mixed_tool: llm.tools.Tool | llm.tools.AsyncTool = mixed_toolkit.get(  # noqa: F841
        empty_ctx, tool_call()
    )
    output: llm.ToolOutput | Awaitable[llm.ToolOutput] = mixed_toolkit.call(  # noqa: F841
        empty_ctx, tool_call()
    )


async def context_toolkit_context_tools():
    empty_ctx = llm.Context()
    sync_toolkit = llm.tools.ContextToolkit(tools=[context_tool])
    expect_context_tool(sync_toolkit.get(empty_ctx, tool_call()))
    assert_type(sync_toolkit.call(empty_ctx, tool_call()), llm.ToolOutput[int])

    async_toolkit = llm.tools.ContextToolkit(tools=[async_context_tool])
    expect_async_context_tool(async_toolkit.get(empty_ctx, tool_call()))
    assert_type(
        async_toolkit.call(empty_ctx, tool_call()), Awaitable[llm.ToolOutput[int]]
    )

    mixed_toolkit = llm.tools.ContextToolkit(tools=[context_tool, async_context_tool])
    mixed_tool: llm.tools.ContextTool | llm.tools.AsyncContextTool = mixed_toolkit.get(  # noqa: F841
        empty_ctx, tool_call()
    )
    output: llm.ToolOutput | Awaitable[llm.ToolOutput] = mixed_toolkit.call(  # noqa: F841
        empty_ctx, tool_call()
    )


async def context_toolkit_mixed():
    empty_ctx = llm.Context()
    sync_toolkit = llm.tools.ContextToolkit(tools=[tool, context_tool])
    maybe_ctx_tool: llm.tools.Tool | llm.tools.ContextTool = sync_toolkit.get(  # noqa: F841
        empty_ctx, tool_call()
    )
    assert_type(sync_toolkit.call(empty_ctx, tool_call()), llm.ToolOutput[int])

    async_toolkit = llm.tools.ContextToolkit(tools=[async_tool, async_context_tool])
    maybe_ctx_async_tool: llm.tools.AsyncTool | llm.tools.AsyncContextTool = (  # noqa: F841
        async_toolkit.get(empty_ctx, tool_call())
    )
    assert_type(
        async_toolkit.call(empty_ctx, tool_call()), Awaitable[llm.ToolOutput[int]]
    )

    mixed_toolkit = llm.tools.ContextToolkit(
        tools=[tool, context_tool, async_tool, async_context_tool]
    )
    maybe_ctx_mixed_tool: (  # noqa: F841
        llm.tools.Tool
        | llm.tools.ContextTool
        | llm.tools.AsyncTool
        | llm.tools.AsyncContextTool
    ) = mixed_toolkit.get(empty_ctx, tool_call())
    output: llm.ToolOutput | Awaitable[llm.ToolOutput] = mixed_toolkit.call(  # noqa: F841
        empty_ctx, tool_call()
    )


async def tools_from_context():
    toolkit = llm.tools.ContextToolkit(tools=[])
    ctx = llm.Context(tools=[tool])
    expect_tool(toolkit.get(ctx, tool_call()))

    toolkit2 = llm.tools.ContextToolkit(tools=[tool])
    ctx2 = llm.Context(tools=[async_context_tool])
    result_tool: llm.tools.Tool | llm.tools.AsyncContextTool = toolkit2.get(  # noqa: F841
        ctx2, tool_call()
    )

    # llm.Context(tools=[None]) is possible due to use of OptionalContextToolT,
    # however the typing for toolkit.get still works:
    ctx3 = llm.Context(tools=[None])
    expect_tool(toolkit2.get(ctx3, tool_call()))
