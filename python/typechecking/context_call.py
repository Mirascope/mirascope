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
    expect_async_context_call,
    expect_context_call,
    prompt,
    tool,
)


def test_context_call_deps_matches_prompt_deps():
    """Verify that @llm.context_call matches DepsT with its prompt"""

    # Type error: Cannot use context call with non-context prompt
    llm.context_call(
        provider="openai",
        model_id="gpt-4o-mini",
    )(prompt)  # pyright: ignore[reportArgumentType, reportCallIssue]

    # Good: Context call and prompt match deps type
    expect_context_call(
        llm.context_call(
            provider="openai",
            model_id="gpt-4o-mini",
        )(context_prompt)
    )

    # Fail: When the tool expects different deps
    llm.context_call(
        provider="openai", model_id="gpt-4o-mini", tools=[context_tool_other_deps]
    )(context_prompt)  # pyright: ignore[reportArgumentType]

    # Fail: When the tool deps are mismatched
    llm.context_call(
        provider="openai",
        model_id="gpt-4o-mini",
        tools=[context_tool, context_tool_other_deps],
    )(context_prompt)  # pyright: ignore[reportCallIssue]


def test_async_context_call_deps():
    """Verify that @llm.context_call matches DepsT with its prompt (async edition)"""

    # Type error: Cannot use context call with non-context prompt
    llm.context_call(
        provider="openai",
        model_id="gpt-4o-mini",
    )(async_prompt)  # pyright: ignore[reportArgumentType, reportCallIssue]

    expect_async_context_call(
        llm.context_call(
            provider="openai",
            model_id="gpt-4o-mini",
        )(async_context_prompt)
    )

    expect_async_context_call(
        llm.context_call(
            provider="openai",
            model_id="gpt-4o-mini",
        )(async_context_prompt)
    )

    llm.context_call(
        provider="openai", model_id="gpt-4o-mini", tools=[async_context_tool]
    )(async_context_prompt)
    # Fail: When the tool has deps but the prompt does not
    llm.context_call(
        provider="openai", model_id="gpt-4o-mini", tools=[async_context_tool]
    )(async_context_prompt)

    # Fail: When the prompt has deps but the tool does not
    llm.context_call(
        provider="openai", model_id="gpt-4o-mini", tools=[async_context_tool]
    )(async_context_prompt)

    # Fail: When the tool expects different context deps entirely
    llm.context_call(
        provider="openai", model_id="gpt-4o-mini", tools=[async_context_tool_other_deps]
    )(async_context_prompt)  # pyright: ignore[reportArgumentType]


async def test_tool_sync_or_async_must_match_prompt():
    """Test only sync tools can be used with a sync prompt"""

    llm.context_call(provider="openai", model_id="gpt-4o-mini")(context_prompt)
    llm.context_call(provider="openai", model_id="gpt-4o-mini", tools=[tool])(
        context_prompt
    )
    # Error: Async tool with sync prompt
    llm.context_call(provider="openai", model_id="gpt-4o-mini", tools=[async_tool])(
        context_prompt  # pyright: ignore[reportArgumentType]
    )
    # Error: Mixed tools with sync prompt
    llm.context_call(
        provider="openai", model_id="gpt-4o-mini", tools=[tool, async_tool]
    )(context_prompt)  # pyright: ignore[reportCallIssue]

    llm.context_call(provider="openai", model_id="gpt-4o-mini")(async_context_prompt)
    llm.context_call(provider="openai", model_id="gpt-4o-mini", tools=[async_tool])(
        async_context_prompt
    )
    # Error: Sync tool with async prompt
    llm.context_call(provider="openai", model_id="gpt-4o-mini", tools=[tool])(
        async_context_prompt  # pyright: ignore[reportArgumentType]
    )
    # Error: Mixed tools with async prompt
    llm.context_call(
        provider="openai", model_id="gpt-4o-mini", tools=[tool, async_tool]
    )(async_context_prompt)  # pyright: ignore[reportCallIssue]
