from mirascope.llm import agents

from .utils import (
    Deps,
    async_prompt,
    async_tool,
    context_prompt,
    context_prompt_deps,
    context_tool,
    context_tool_deps,
    prompt,
    tool,
    tool_other_deps,
)


def test_agent_prompt_deps():
    x1: agents.AgentTemplate[None] = agents.agent(  # noqa: F841
        provider="openai",
        model_id="gpt-4o-mini",
    )(prompt)
    x2: agents.AgentTemplate[None] = agents.agent(  # noqa: F841
        provider="openai",
        model_id="gpt-4o-mini",
    )(context_prompt)
    x3: agents.AgentTemplate[Deps] = agents.agent(  # noqa: F841
        provider="openai",
        model_id="gpt-4o-mini",
    )(context_prompt_deps)


def test_sync_async_agent():
    def expect_sync(x: agents.AgentTemplate): ...
    def expect_async(x: agents.AsyncAgentTemplate): ...

    expect_sync(
        agents.agent(
            provider="openai",
            model_id="gpt-4o-mini",
        )(prompt)
    )
    expect_sync(
        agents.agent(provider="openai", model_id="gpt-4o-mini", tools=[tool])(prompt)
    )

    # Expected type error: async tool can't be used with sync prompt
    agents.agent(provider="openai", model_id="gpt-4o-mini", tools=[async_tool])(prompt)  # pyright: ignore[reportArgumentType]

    expect_async(
        agents.agent(
            provider="openai",
            model_id="gpt-4o-mini",
        )(async_prompt)
    )
    expect_async(
        agents.agent(provider="openai", model_id="gpt-4o-mini", tools=[async_tool])(
            async_prompt
        )
    )

    # Expected type error: sync tool can't be used with async prompt
    agents.agent(provider="openai", model_id="gpt-4o-mini", tools=[tool])(async_prompt)  # pyright: ignore[reportArgumentType]


def test_agent_tool_deps():
    x1: agents.AgentTemplate[None] = agents.agent(  # noqa: F841
        provider="openai", model_id="gpt-4o-mini", tools=[context_tool]
    )(context_prompt)

    x2: agents.AgentTemplate[Deps] = agents.agent(  # noqa: F841
        provider="openai", model_id="gpt-4o-mini", tools=[context_tool_deps]
    )(context_prompt_deps)

    # deps mismatch between the context_tool and the context_prompt_deps
    agents.AgentTemplate = agents.agent(
        provider="openai", model_id="gpt-4o-mini", tools=[context_tool]
    )(
        context_prompt_deps  # pyright: ignore[reportArgumentType]
    )

    # type mismatch between tool_other_deps and context_prompt_deps
    agents.AgentTemplate = agents.agent(
        provider="openai", model_id="gpt-4o-mini", tools=[tool_other_deps]
    )(
        context_prompt_deps  # pyright: ignore[reportArgumentType]
    )

    # deps mismatch between context_tool_deps and tool_other_deps
    agents.AgentTemplate = agents.agent(
        provider="openai",
        model_id="gpt-4o-mini",
        tools=[context_tool_deps, tool_other_deps],
    )(context_prompt_deps)  # pyright: ignore[reportCallIssue]
