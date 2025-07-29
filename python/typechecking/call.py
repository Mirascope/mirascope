from collections.abc import Awaitable

from typing_extensions import assert_type

from mirascope import llm

from .utils import (
    async_context_prompt_deps,
    async_prompt,
    async_tool,
    context_prompt,
    context_prompt_deps,
    expect_async_call,
    expect_call,
    prompt,
    tool,
    tool_call,
)


def test_call():
    """Verify that @llm.call works as expected"""
    # Verify that regular prompts become regular calls,
    expect_call(llm.call("openai:gpt-4o-mini")(prompt))

    # Verify that async prompts become async calls,
    async_call = llm.call("openai:gpt-4o-mini")(async_prompt)
    expect_async_call(async_call)

    # Nothing stops you from making a regular call from a context prompt, tho it is confusing
    deceptive_call = llm.call("openai:gpt-4o-mini")(context_prompt)
    expect_call(deceptive_call)


async def test_tool_type_propagation():
    """Test sync/async tool distinction makes it thru call"""
    stk = llm.call("openai:gpt-4o-mini", tools=[tool])(context_prompt_deps).toolkit

    assert_type(stk.call(tool_call()), llm.ToolOutput[int])

    atk = llm.call("openai:gpt-4o-mini", tools=[async_tool])(
        context_prompt_deps
    ).toolkit
    assert_type(await atk.call(tool_call()), llm.ToolOutput[int])

    mtk = llm.call("openai:gpt-4o-mini", tools=[tool, async_tool])(
        context_prompt_deps
    ).toolkit
    assert_type(
        mtk.call(tool_call()), llm.ToolOutput[int] | Awaitable[llm.ToolOutput[int]]
    )


async def test_tool_type_propagation_async_prompt():
    """Test sync/async tool distinction makes it thru call with async prompt"""
    stk = llm.call("openai:gpt-4o-mini", tools=[tool])(
        async_context_prompt_deps
    ).toolkit

    assert_type(stk.call(tool_call()), llm.ToolOutput[int])

    atk = llm.call("openai:gpt-4o-mini", tools=[async_tool])(
        async_context_prompt_deps
    ).toolkit
    assert_type(await atk.call(tool_call()), llm.ToolOutput[int])

    mtk = llm.call("openai:gpt-4o-mini", tools=[tool, async_tool])(
        async_context_prompt_deps
    ).toolkit
    assert_type(
        mtk.call(tool_call()), llm.ToolOutput[int] | Awaitable[llm.ToolOutput[int]]
    )
