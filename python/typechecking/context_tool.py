"""Type safety testing for tools and context tools"""

from mirascope import llm

from .utils import (
    Deps,
    OtherDeps,
    expect_context_tool_deps,
)


def no_context() -> int:
    return 42


def no_deps(ctx: llm.Context) -> int:
    return 42


def with_deps(ctx: llm.Context[Deps]) -> int:
    return 42


async def async_no_context() -> int:
    return 42


async def async_no_deps(ctx: llm.Context) -> int:
    return 42


def deps_mismatch_failures():
    llm.context_tool(no_context)  # type: ignore[reportCallIssue]
    llm.context_tool(no_deps, deps_type=Deps)  # type: ignore[reportCallIssue]
    llm.context_tool(async_no_context)  # type: ignore[reportCallIssue]
    llm.context_tool(async_no_deps, deps_type=Deps)  # type: ignore[reportCallIssue]


def deps_arg_must_match():
    # Good:
    expect_context_tool_deps(llm.context_tool(deps_type=Deps)(with_deps))
    expect_context_tool_deps(llm.context_tool(with_deps))  # Inference

    # Bad:
    expect_context_tool_deps(llm.context_tool(deps_type=OtherDeps)(with_deps))  # type: ignore[reportCallIssue]
    expect_context_tool_deps(llm.context_tool(with_deps, deps_type=OtherDeps))  # type: ignore[reportCallIssue]
