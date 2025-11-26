from typing import Any

from mirascope.llm import agents

from .utils import (
    Deps,
    async_prompt,
    async_tool,
    context_prompt,
    context_tool,
    context_tool_other_deps,
    prompt,
    tool,
)


def test_agent_prompt_deps():
    x1: agents.AgentTemplate[None] = agents.agent(  # noqa: F841
        provider="openai:completions",
        model_id="gpt-4o-mini",
    )(prompt)

    x3: agents.AgentTemplate[Deps] = agents.agent(  # noqa: F841
        provider="openai:completions",
        model_id="gpt-4o-mini",
    )(context_prompt)


def test_sync_async_agent():
    def expect_sync(x: agents.AgentTemplate[Any]): ...
    def expect_async(x: agents.AsyncAgentTemplate[Any]): ...

    expect_sync(
        agents.agent(
            provider="openai:completions",
            model_id="gpt-4o-mini",
        )(prompt)
    )
    expect_sync(
        agents.agent(
            provider="openai:completions", model_id="gpt-4o-mini", tools=[tool]
        )(prompt)
    )

    # Expected type error: async tool can't be used with sync prompt
    agents.agent(
        provider="openai:completions", model_id="gpt-4o-mini", tools=[async_tool]
    )(prompt)  # pyright: ignore[reportArgumentType]

    expect_async(
        agents.agent(
            provider="openai:completions",
            model_id="gpt-4o-mini",
        )(async_prompt)
    )
    expect_async(
        agents.agent(
            provider="openai:completions", model_id="gpt-4o-mini", tools=[async_tool]
        )(async_prompt)
    )

    # Expected type error: sync tool can't be used with async prompt
    agents.agent(provider="openai:completions", model_id="gpt-4o-mini", tools=[tool])(
        async_prompt  # pyright: ignore[reportArgumentType]
    )


def test_agent_tool_deps():
    x1: agents.AgentTemplate[Deps] = agents.agent(  # noqa: F841
        provider="openai:completions", model_id="gpt-4o-mini", tools=[context_tool]
    )(context_prompt)

    # deps mismatch between the context_tool and the context_prompt
    agents.AgentTemplate = agents.agent(
        provider="openai:completions",
        model_id="gpt-4o-mini",
        tools=[context_tool_other_deps],
    )(
        context_prompt  # pyright: ignore[reportArgumentType]
    )

    # deps mismatch between context_tool_deps and tool_other_deps
    agents.AgentTemplate = agents.agent(
        provider="openai:completions",
        model_id="gpt-4o-mini",
        tools=[context_tool, context_tool_other_deps],
    )(context_prompt)  # pyright: ignore[reportCallIssue]
