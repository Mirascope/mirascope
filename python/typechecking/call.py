from mirascope import llm

from .utils import (
    async_context_prompt,
    async_context_prompt_deps,
    async_prompt,
    context_prompt,
    context_prompt_deps,
    expect_async_call,
    expect_async_context_call,
    expect_async_context_call_deps,
    expect_call,
    expect_context_call,
    expect_context_call_deps,
    prompt,
)


def test_non_context_calls():
    """Verify that @llm.call works as expected"""
    # Verify that regular prompts become regular calls,
    expect_call(llm.call("openai:gpt-4o-mini")(prompt))

    # Verify that async prompts become async calls,
    async_call = llm.call("openai:gpt-4o-mini")(async_prompt)
    expect_async_call(async_call)

    # Nothing stops you from making a regular call from a context prompt, tho it is confusing
    deceptive_call = llm.call("openai:gpt-4o-mini")(context_prompt)
    expect_call(deceptive_call)


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

    expect_async_context_call(
        llm.context_call("openai:gpt-4o-mini")(async_context_prompt)
    )


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
