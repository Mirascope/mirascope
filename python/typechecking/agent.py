from mirascope import llm

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
    x1: llm.AgentTemplate[None] = llm.agent("openai:gpt-4o-mini")(prompt)  # noqa: F841
    x2: llm.AgentTemplate[None] = llm.agent("openai:gpt-4o-mini")(context_prompt)  # noqa: F841
    x3: llm.AgentTemplate[Deps] = llm.agent("openai:gpt-4o-mini")(context_prompt_deps)  # noqa: F841


def test_sync_async_agent():
    def expect_sync(x: llm.AgentTemplate): ...
    def expect_async(x: llm.AsyncAgentTemplate): ...

    expect_sync(llm.agent("openai:gpt-4o-mini")(prompt))
    expect_sync(llm.agent("openai:gpt-4o-mini", tools=[tool, async_tool])(prompt))

    expect_async(llm.agent("openai:gpt-4o-mini")(async_prompt))
    expect_async(
        llm.agent("openai:gpt-4o-mini", tools=[tool, async_tool])(async_prompt)
    )


def test_agent_tool_deps():
    x1: llm.AgentTemplate[None] = llm.agent("openai:gpt-4o-mini", tools=[context_tool])(  # noqa: F841
        context_prompt
    )

    x2: llm.AgentTemplate[Deps] = llm.agent(  # noqa: F841
        "openai:gpt-4o-mini", tools=[context_tool_deps]
    )(context_prompt_deps)

    llm.AgentTemplate = llm.agent("openai:gpt-4o-mini", tools=[context_tool])(
        context_prompt_deps  # type: ignore[reportCallIssue]
    )
    llm.AgentTemplate = llm.agent("openai:gpt-4o-mini", tools=[tool_other_deps])(
        context_prompt_deps  # type: ignore[reportCallIssue]
    )

    llm.AgentTemplate = llm.agent(
        "openai:gpt-4o-mini", tools=[context_tool_deps, tool_other_deps]
    )(context_prompt_deps)  # type: ignore[reportCallIssue]
