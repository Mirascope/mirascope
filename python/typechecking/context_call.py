from collections.abc import Awaitable

from typing_extensions import assert_type

from mirascope import llm

from .utils import (
    Deps,
    async_context_prompt,
    async_context_prompt_deps,
    async_prompt,
    async_tool,
    context_prompt,
    context_prompt_deps,
    context_tool,
    context_tool_deps,
    expect_async_context_call,
    expect_async_context_call_deps,
    expect_context_call,
    expect_context_call_deps,
    prompt,
    tool_call,
    tool_other_deps,
)


def test_context_call_deps_matches_prompt_deps():
    """Verify that @llm.context_call matches DepsT with its prompt"""

    # Type error: Cannot use context call with non-context prompt
    llm.context_call("openai:gpt-4o-mini")(prompt)  # type: ignore[reportCallIssue]

    # Good: Context call (no deps) with context prompt (no deps)
    expect_context_call(llm.context_call("openai:gpt-4o-mini")(context_prompt))

    # Good: Match deps type between decorator and prompt
    expect_context_call_deps(
        llm.context_call("openai:gpt-4o-mini")(context_prompt_deps)
    )

    llm.context_call("openai:gpt-4o-mini", tools=[context_tool_deps])(
        context_prompt_deps
    )
    # Fail: When the tool has deps but the prompt does not
    llm.context_call("openai:gpt-4o-mini", tools=[context_tool_deps])(context_prompt)  # type: ignore[reportCallIssue]

    # Fail: When the prompt has deps but the tool does not
    llm.context_call("openai:gpt-4o-mini", tools=[context_tool])(context_prompt_deps)  # type: ignore[reportCallIssue]

    # Fail: When the tool expects different context deps entirely
    llm.context_call("openai:gpt-4o-mini", tools=[tool_other_deps])(context_prompt_deps)  # type: ignore[reportCallIssue]


def test_async_context_call_deps():
    """Verify that @llm.context_call matches DepsT with its prompt (async edition)"""

    # Type error: Cannot use context call with non-context prompt
    llm.context_call("openai:gpt-4o-mini")(async_prompt)  # type: ignore[reportCallIssue]

    expect_async_context_call(
        llm.context_call("openai:gpt-4o-mini")(async_context_prompt)
    )

    expect_async_context_call_deps(
        llm.context_call("openai:gpt-4o-mini")(async_context_prompt_deps)
    )

    llm.context_call("openai:gpt-4o-mini", tools=[context_tool_deps])(
        async_context_prompt_deps
    )
    # Fail: When the tool has deps but the prompt does not
    llm.context_call("openai:gpt-4o-mini", tools=[context_tool_deps])(
        async_context_prompt  # type: ignore[reportCallIssue]
    )

    # Fail: When the prompt has deps but the tool does not
    llm.context_call("openai:gpt-4o-mini", tools=[context_tool])(
        async_context_prompt_deps  # type: ignore[reportCallIssue]
    )

    # Fail: When the tool expects different context deps entirely
    llm.context_call("openai:gpt-4o-mini", tools=[tool_other_deps])(
        async_context_prompt_deps  # type: ignore[reportCallIssue]
    )


async def test_tool_type_propagation():
    """Test sync/async tool distinction makes it thru context_call"""
    stk = llm.context_call("openai:gpt-4o-mini", tools=[context_tool_deps])(
        context_prompt_deps
    ).toolkit

    ctx = llm.Context(deps=Deps())
    assert_type(stk.call(ctx, tool_call()), llm.ToolOutput[int])

    atk = llm.context_call("openai:gpt-4o-mini", tools=[async_tool])(
        context_prompt_deps
    ).toolkit
    assert_type(await atk.call(ctx, tool_call()), llm.ToolOutput[int])

    mtk = llm.context_call("openai:gpt-4o-mini", tools=[context_tool_deps, async_tool])(
        context_prompt_deps
    ).toolkit
    assert_type(
        mtk.call(ctx, tool_call()), llm.ToolOutput[int] | Awaitable[llm.ToolOutput[int]]
    )


async def test_tool_type_propagation_async_prompt():
    """Test sync/async tool distinction makes it thru context_call with async prompt"""
    stk = llm.context_call("openai:gpt-4o-mini", tools=[context_tool_deps])(
        async_context_prompt_deps
    ).toolkit

    ctx = llm.Context(deps=Deps())
    assert_type(stk.call(ctx, tool_call()), llm.ToolOutput[int])

    atk = llm.context_call("openai:gpt-4o-mini", tools=[async_tool])(
        async_context_prompt_deps
    ).toolkit
    assert_type(await atk.call(ctx, tool_call()), llm.ToolOutput[int])

    mtk = llm.context_call("openai:gpt-4o-mini", tools=[context_tool_deps, async_tool])(
        async_context_prompt_deps
    ).toolkit
    assert_type(
        mtk.call(ctx, tool_call()), llm.ToolOutput[int] | Awaitable[llm.ToolOutput[int]]
    )
