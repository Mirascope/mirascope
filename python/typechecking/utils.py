from dataclasses import dataclass
from typing import Any

from mirascope import llm


@dataclass
class Deps: ...


@dataclass
class OtherDeps: ...


def prompt() -> str:
    return "hello world"


def context_prompt(ctx: llm.Context) -> str:
    return "hello world"


def context_prompt_deps(ctx: llm.Context[Deps]) -> str:
    return "hello world"


async def async_prompt() -> str:
    return "hello world"


async def async_context_prompt(ctx: llm.Context) -> str:
    return "hello world"


async def async_context_prompt_deps(ctx: llm.Context[Deps]) -> str:
    return "hello world"


def tool_call() -> llm.content.ToolCall:
    raise NotImplementedError()


@llm.tool
def tool() -> int:
    return 41


@llm.context_tool
def context_tool(ctx: llm.Context) -> int:
    return 42


@llm.context_tool
def context_tool_deps(ctx: llm.Context[Deps]) -> int:
    return 43


@llm.tool
async def async_tool() -> int:
    return 41


@llm.context_tool
async def async_context_tool(ctx: llm.Context) -> int:
    return 42


@llm.context_tool
async def async_context_tool_deps(ctx: llm.Context[Deps]) -> int:
    return 43


def expect_call(x: llm.calls.Call): ...
def expect_context_call(x: llm.calls.ContextCall): ...
def expect_context_call_deps(x: llm.calls.ContextCall[..., Any, Any, Deps]): ...
def expect_async_call(x: llm.calls.AsyncCall): ...
def expect_async_context_call(x: llm.calls.AsyncContextCall): ...
def expect_async_context_call_deps(
    x: llm.calls.AsyncContextCall[..., Any, Any, Deps],
): ...


def expect_tool(x: llm.tools.Tool): ...
def expect_context_tool(x: llm.tools.ContextTool): ...
def expect_context_tool_deps(x: llm.tools.ContextTool[Any, Any, Deps]): ...
def expect_async_tool(x: llm.tools.AsyncTool): ...
def expect_async_context_tool(x: llm.tools.AsyncContextTool): ...
def expect_async_context_tool_deps(x: llm.tools.AsyncContextTool[Any, Any, Deps]): ...


def sanity_checks():
    expect_tool(tool)
    expect_context_tool(context_tool)
    expect_context_tool_deps(context_tool_deps)

    expect_async_tool(async_tool)
    expect_async_context_tool(async_context_tool)
    expect_async_context_tool_deps(async_context_tool_deps)
