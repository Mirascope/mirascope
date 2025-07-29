from typing_extensions import assert_type

from mirascope import llm

from .utils import (
    Deps,
    OtherDeps,
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
    llm.agent("openai:gpt-4o-mini")(prompt)
    llm.agent("openai:gpt-4o-mini")(context_prompt)
    llm.agent("openai:gpt-4o-mini", deps_type=Deps)(prompt)
    llm.agent("openai:gpt-4o-mini", deps_type=Deps)(context_prompt_deps)

    llm.agent("openai:gpt-4o-mini")(context_prompt_deps)  # type: ignore[reportCallIssue]
    llm.agent("openai:gpt-4o-mini", deps_type=OtherDeps)(context_prompt_deps)  # type: ignore[reportCallIssue]


def test_sync_async_agent():
    assert_type(llm.agent("openai:gpt-4o-mini")(prompt), llm.agents.AgentTemplate)
    assert_type(
        llm.agent("openai:gpt-4o-mini", tools=[tool])(prompt), llm.agents.AgentTemplate
    )
    assert_type(
        llm.agent("openai:gpt-4o-mini", tools=[tool, async_tool])(prompt),
        llm.agents.AsyncAgentTemplate,
    )
    assert_type(
        llm.agent("openai:gpt-4o-mini", tools=[async_tool])(prompt),
        llm.agents.AsyncAgentTemplate,
    )
    assert_type(
        llm.agent("openai:gpt-4o-mini")(async_prompt),
        llm.agents.AsyncAgentTemplate,
    )
    assert_type(
        llm.agent("openai:gpt-4o-mini", tools=[tool])(async_prompt),
        llm.agents.AsyncAgentTemplate,
    )


def test_agent_tool_deps():
    llm.agent("openai:gpt-4o-mini", tools=[context_tool], deps_type=type(None))(
        context_prompt
    )

    llm.agent("openai:gpt-4o-mini", tools=[context_tool_deps], deps_type=Deps)(
        context_prompt_deps
    )
    llm.agent("openai:gpt-4o-mini", tools=[context_tool], deps_type=Deps)(  # type: ignore[reportCallIssue]
        context_prompt_deps
    )
    llm.agent("openai:gpt-4o-mini", tools=[tool_other_deps], deps_type=Deps)(  # type: ignore[reportCallIssue]
        context_prompt_deps
    )
