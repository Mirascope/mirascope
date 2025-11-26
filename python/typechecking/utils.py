from dataclasses import dataclass

from mirascope import llm


@dataclass
class Deps:
    bar: int


@dataclass
class OtherDeps:
    foo: str


def prompt() -> str:
    return "hello world"


def context_prompt(ctx: llm.Context[Deps]) -> str:
    return "hello world"


async def async_prompt() -> str:
    return "hello world"


async def async_context_prompt(ctx: llm.Context[Deps]) -> str:
    return "hello world"


def context() -> llm.Context[Deps]:
    return llm.Context(deps=Deps(bar=3))


@llm.tool
def tool() -> int:
    return 41


@llm.tool
def context_tool(ctx: llm.Context[Deps]) -> int:
    return 42


@llm.tool
async def async_tool() -> int:
    return 41


@llm.tool
async def async_context_tool(ctx: llm.Context[Deps]) -> int:
    return 42


@llm.tool
def context_tool_other_deps(ctx: llm.Context[OtherDeps]):
    return 41


@llm.tool
async def async_context_tool_other_deps(ctx: llm.Context[OtherDeps]):
    return 41


def tool_call() -> llm.ToolCall:
    raise NotImplementedError()


def expect_call(x: llm.calls.Call[...]): ...
def expect_async_call(x: llm.calls.AsyncCall[...]): ...
def expect_context_call(x: llm.calls.ContextCall[..., Deps]): ...
def expect_async_context_call(x: llm.calls.AsyncContextCall[..., Deps]): ...


def expect_tool(x: llm.tools.Tool): ...
def expect_async_tool(x: llm.tools.AsyncTool): ...
def expect_context_tool(x: llm.tools.ContextTool[Deps]): ...
def expect_async_context_tool(x: llm.tools.AsyncContextTool[Deps]): ...


def sanity_checks():
    expect_tool(tool)
    expect_context_tool(context_tool)

    expect_async_tool(async_tool)
    expect_async_context_tool(async_context_tool)
