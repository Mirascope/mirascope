from mirascope import llm

from .utils import (
    async_context_prompt,
    async_context_tool,
    async_context_tool_other_deps,
    async_prompt,
    async_tool,
    context_prompt,
    context_tool,
    context_tool_other_deps,
    expect_async_call,
    expect_async_context_call,
    expect_call,
    expect_context_call,
    prompt,
    tool,
)


def test_call():
    """Verify that @llm.call works as expected"""
    # Verify that regular prompts become regular calls,
    expect_call(llm.call("openai/gpt-5-mini")(prompt))

    # Verify that async prompts become async calls,
    async_call = llm.call(
        "openai/gpt-5-mini",
    )(async_prompt)
    expect_async_call(async_call)

    # If there is a context prompt, it will become a context call
    context_call = llm.call(
        "openai/gpt-5-mini",
    )(context_prompt)
    expect_context_call(context_call)


async def test_tool_sync_or_async_must_match_prompt():
    """Test only sync tools can be used with a sync prompt"""

    llm.call("openai/gpt-5-mini")(prompt)
    llm.call("openai/gpt-5-mini", tools=[tool])(prompt)

    # Error: Async tool with sync prompt
    llm.call("openai/gpt-5-mini", tools=[async_tool])(
        prompt  # pyright: ignore[reportArgumentType, reportCallIssue]
    )
    # Error: Sync tool and async tool mixed with sync prompt
    llm.call(
        "openai/gpt-5-mini",
        tools=[tool, async_tool],
    )(prompt)  # pyright: ignore[reportCallIssue]

    llm.call("openai/gpt-5-mini")(async_prompt)
    llm.call("openai/gpt-5-mini", tools=[async_tool])(async_prompt)
    # Error: Sync tool with async prompt
    llm.call("openai/gpt-5-mini", tools=[tool])(
        async_prompt  # pyright: ignore[reportArgumentType,reportCallIssue]
    )
    # Error: Mixed tools with async prompt
    llm.call(
        "openai/gpt-5-mini",
        tools=[tool, async_tool],
    )(async_prompt)  # pyright: ignore[reportCallIssue]

    llm.call("openai/gpt-5-mini")(context_prompt)
    llm.call("openai/gpt-5-mini", tools=[tool])(context_prompt)
    # Error: Async tool with sync prompt
    llm.call("openai/gpt-5-mini", tools=[async_tool])(
        context_prompt  # pyright: ignore[reportCallIssue,reportArgumentType]
    )
    # Error: Mixed tools with sync prompt
    llm.call(
        "openai/gpt-5-mini",
        tools=[tool, async_tool],
    )(context_prompt)  # pyright: ignore[reportCallIssue]

    llm.call("openai/gpt-5-mini")(async_context_prompt)
    llm.call("openai/gpt-5-mini", tools=[async_tool])(async_context_prompt)
    # Error: Sync tool with async prompt
    llm.call("openai/gpt-5-mini", tools=[tool])(
        async_context_prompt  # pyright: ignore[reportCallIssue,reportArgumentType]
    )
    # Error: Mixed tools with async prompt
    llm.call(
        "openai/gpt-5-mini",
        tools=[tool, async_tool],
    )(async_context_prompt)  # pyright: ignore[reportCallIssue]


def test_context_call_deps_matches_prompt_deps():
    """Verify that @llm.call matches DepsT with its prompt"""

    # Good: Context call and prompt match deps type
    expect_context_call(llm.call("openai/gpt-5-mini")(context_prompt))

    # Fail: When the tool expects different deps
    llm.call(
        "openai/gpt-5-mini",
        tools=[context_tool_other_deps],
    )(context_prompt)  # pyright: ignore[reportArgumentType]

    # Fail: When the tool deps are mismatched
    llm.call(
        "openai/gpt-5-mini",
        tools=[context_tool, context_tool_other_deps],
    )(context_prompt)  # pyright: ignore[reportCallIssue]


def test_async_context_call_deps():
    """Verify that @llm.call matches DepsT with its prompt (async edition)"""

    expect_async_context_call(llm.call("openai/gpt-5-mini")(async_context_prompt))

    expect_async_context_call(llm.call("openai/gpt-5-mini")(async_context_prompt))

    llm.call(
        "openai/gpt-5-mini",
        tools=[async_context_tool],
    )(async_context_prompt)
    # Fail: When the tool has deps but the prompt does not
    llm.call(
        "openai/gpt-5-mini",
        tools=[async_context_tool],
    )(async_context_prompt)

    # Fail: When the prompt has deps but the tool does not
    llm.call(
        "openai/gpt-5-mini",
        tools=[async_context_tool],
    )(async_context_prompt)

    # Fail: When the tool expects different context deps entirely
    llm.call(
        "openai/gpt-5-mini",
        tools=[async_context_tool_other_deps],
    )(async_context_prompt)  # pyright: ignore[reportArgumentType]
