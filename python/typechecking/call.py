from mirascope import llm

from .utils import (
    async_prompt,
    async_tool,
    context_prompt,
    expect_async_call,
    expect_call,
    prompt,
    tool,
)


def test_call():
    """Verify that @llm.call works as expected"""
    # Verify that regular prompts become regular calls,
    expect_call(
        llm.call(
            provider="openai",
            model_id="gpt-4o-mini",
        )(prompt)
    )

    # Verify that async prompts become async calls,
    async_call = llm.call(
        provider="openai",
        model_id="gpt-4o-mini",
    )(async_prompt)
    expect_async_call(async_call)

    # Nothing stops you from making a regular call from a context prompt, tho it is confusing
    deceptive_call = llm.call(
        provider="openai",
        model_id="gpt-4o-mini",
    )(context_prompt)
    expect_call(deceptive_call)


async def test_tool_sync_or_async_must_match_prompt():
    """Test only sync tools can be used with a sync prompt"""

    llm.call(provider="openai", model_id="gpt-4o-mini")(prompt)
    llm.call(provider="openai", model_id="gpt-4o-mini", tools=[tool])(prompt)
    llm.call(provider="openai", model_id="gpt-4o-mini", tools=[async_tool])(prompt)  # type: ignore[reportArgumentType]
    llm.call(provider="openai", model_id="gpt-4o-mini", tools=[tool, async_tool])(
        prompt
    )  # type: ignore[reportArgumentType]

    llm.call(provider="openai", model_id="gpt-4o-mini")(async_prompt)
    llm.call(provider="openai", model_id="gpt-4o-mini", tools=[async_tool])(
        async_prompt
    )
    llm.call(provider="openai", model_id="gpt-4o-mini", tools=[tool])(async_prompt)  # type: ignore[reportArgumentType]
    llm.call(provider="openai", model_id="gpt-4o-mini", tools=[tool, async_tool])(
        async_prompt
    )  # type: ignore[reportArgumentType]
