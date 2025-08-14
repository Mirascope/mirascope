from mirascope import llm

from .utils import (
    async_context_prompt,
    async_context_prompt_deps,
    async_context_tool,
    async_context_tool_deps,
    async_prompt,
    async_tool,
    async_tool_other_deps,
    context_prompt,
    context_prompt_deps,
    context_tool,
    context_tool_deps,
    expect_async_context_call,
    expect_async_context_call_deps,
    expect_context_call,
    expect_context_call_deps,
    prompt,
    tool,
    tool_other_deps,
)


def test_context_call_deps_matches_prompt_deps():
    """Verify that @llm.context_call matches DepsT with its prompt"""

    # Type error: Cannot use context call with non-context prompt
    llm.context_call(
        provider="openai",
        model="gpt-4o-mini",
    )(prompt)  # type: ignore[reportCallIssue]

    # Good: Context call (no deps) with context prompt (no deps)
    expect_context_call(
        llm.context_call(
            provider="openai",
            model="gpt-4o-mini",
        )(context_prompt)
    )

    # Good: Match deps type between decorator and prompt
    expect_context_call_deps(
        llm.context_call(
            provider="openai",
            model="gpt-4o-mini",
        )(context_prompt_deps)
    )

    llm.context_call(provider="openai", model="gpt-4o-mini", tools=[context_tool_deps])(
        context_prompt_deps
    )
    # Fail: When the tool has deps but the prompt does not
    llm.context_call(provider="openai", model="gpt-4o-mini", tools=[context_tool_deps])(
        context_prompt  # type: ignore[reportCallIssue]
    )

    # Fail: When the prompt has deps but the tool does not
    llm.context_call(provider="openai", model="gpt-4o-mini", tools=[context_tool])(
        context_prompt_deps  # type: ignore[reportCallIssue]
    )

    # Fail: When the tool expects different context deps entirely
    llm.context_call(provider="openai", model="gpt-4o-mini", tools=[tool_other_deps])(
        context_prompt_deps  # type: ignore[reportCallIssue]
    )


def test_async_context_call_deps():
    """Verify that @llm.context_call matches DepsT with its prompt (async edition)"""

    # Type error: Cannot use context call with non-context prompt
    llm.context_call(
        provider="openai",
        model="gpt-4o-mini",
    )(async_prompt)  # type: ignore[reportCallIssue]

    expect_async_context_call(
        llm.context_call(
            provider="openai",
            model="gpt-4o-mini",
        )(async_context_prompt)
    )

    expect_async_context_call_deps(
        llm.context_call(
            provider="openai",
            model="gpt-4o-mini",
        )(async_context_prompt_deps)
    )

    llm.context_call(
        provider="openai", model="gpt-4o-mini", tools=[async_context_tool_deps]
    )(async_context_prompt_deps)
    # Fail: When the tool has deps but the prompt does not
    llm.context_call(
        provider="openai", model="gpt-4o-mini", tools=[async_context_tool_deps]
    )(
        async_context_prompt  # type: ignore[reportCallIssue]
    )

    # Fail: When the prompt has deps but the tool does not
    llm.context_call(
        provider="openai", model="gpt-4o-mini", tools=[async_context_tool]
    )(
        async_context_prompt_deps  # type: ignore[reportCallIssue]
    )

    # Fail: When the tool expects different context deps entirely
    llm.context_call(
        provider="openai", model="gpt-4o-mini", tools=[async_tool_other_deps]
    )(
        async_context_prompt_deps  # type: ignore[reportCallIssue]
    )


async def test_tool_sync_or_async_must_match_prompt():
    """Test only sync tools can be used with a sync prompt"""

    llm.context_call(provider="openai", model="gpt-4o-mini")(context_prompt)
    llm.context_call(provider="openai", model="gpt-4o-mini", tools=[tool])(
        context_prompt
    )
    llm.context_call(provider="openai", model="gpt-4o-mini", tools=[async_tool])(
        context_prompt  # type: ignore[reportArgumentType]
    )
    llm.context_call(provider="openai", model="gpt-4o-mini", tools=[tool, async_tool])(
        context_prompt  # type: ignore[reportArgumentType]
    )

    llm.context_call(provider="openai", model="gpt-4o-mini")(async_context_prompt)
    llm.context_call(provider="openai", model="gpt-4o-mini", tools=[async_tool])(
        async_context_prompt
    )
    llm.context_call(provider="openai", model="gpt-4o-mini", tools=[tool])(
        async_context_prompt  # type: ignore[reportArgumentType]
    )
    llm.context_call(provider="openai", model="gpt-4o-mini", tools=[tool, async_tool])(
        async_context_prompt  # type: ignore[reportArgumentType]
    )
