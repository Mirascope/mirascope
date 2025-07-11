"""The `llm.agent` decorator for turning a function into an agent."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol, overload

from ..context import Context
from ..tools import ContextToolDef, ToolDef
from .agent import Agent
from .async_agent import AsyncAgent

if TYPE_CHECKING:
    from ..clients import (
        REGISTERED_LLMS,
    )

from ..types import DepsT, FormatT, P

NoneType = type(None)


class SystemPrompt(Protocol[P, DepsT]):
    """Protocol for a prompt template function that returns a system prompt as a string."""

    def __call__(self, ctx: Context[DepsT]) -> str: ...


class AsyncSystemPrompt(Protocol[P, DepsT]):
    """Protocol for an async prompt template function that returns a system prompt as a string."""

    async def __call__(self, ctx: Context[DepsT]) -> str: ...


class AgentDecorator(Protocol[DepsT, FormatT]):
    """Protocol for the `agent` decorator."""

    @overload
    def __call__(self, fn: AsyncSystemPrompt[P, DepsT]) -> AsyncAgent[DepsT, FormatT]:
        """Decorator for creating an async only agent."""
        ...

    @overload
    def __call__(self, fn: SystemPrompt[P, DepsT]) -> Agent[DepsT, FormatT]:
        """Decorator for creating an agent."""
        ...

    def __call__(
        self, fn: SystemPrompt[P, DepsT] | AsyncSystemPrompt[P, DepsT]
    ) -> Agent[DepsT, FormatT] | AsyncAgent[DepsT, FormatT]:
        """Decorator for creating an agent."""
        ...




# @overload
# def agent(
#     model: ANTHROPIC_REGISTERED_LLMS,
#     *,
#     deps_type: type[DepsT] = NoneType,
#     tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
#     response_format: None = None,
#     client: AnthropicClient | None = None,
#     **params: Unpack[AnthropicParams],
# ) -> AgentDecorator[DepsT, None]:
#     """Overload for Anthropic agents."""
#     ...


# @overload
# def agent(
#     model: ANTHROPIC_REGISTERED_LLMS,
#     *,
#     deps_type: type[DepsT] = NoneType,
#     tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
#     response_format: type[T],
#     client: AnthropicClient | None = None,
#     **params: Unpack[AnthropicParams],
# ) -> StructuredAgentDecorator[DepsT, T]:
#     """Overload for Anthropic agents with response format."""
#     ...


# @overload
# def agent(
#     model: GOOGLE_REGISTERED_LLMS,
#     *,
#     deps_type: type[DepsT] = NoneType,
#     tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
#     response_format: None = None,
#     client: GoogleClient | None = None,
#     **params: Unpack[GoogleParams],
# ) -> AgentDecorator[DepsT, None]:
#     """Overload for Google agents."""
#     ...


# @overload
# def agent(
#     model: GOOGLE_REGISTERED_LLMS,
#     *,
#     deps_type: type[DepsT] = NoneType,
#     tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
#     response_format: type[T],
#     client: GoogleClient | None = None,
#     **params: Unpack[GoogleParams],
# ) -> StructuredAgentDecorator[DepsT, T]:
#     """Overload for Google agents with response format."""
#     ...


# @overload
# def agent(
#     model: OPENAI_REGISTERED_LLMS,
#     *,
#     deps_type: type[DepsT] = NoneType,
#     tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
#     response_format: None = None,
#     client: OpenAIClient | None = None,
#     **params: Unpack[OpenAIParams],
# ) -> AgentDecorator[DepsT, None]:
#     """Overload for OpenAI agents."""
#     ...


# @overload
# def agent(
#     model: OPENAI_REGISTERED_LLMS,
#     *,
#     deps_type: type[DepsT] = NoneType,
#     tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
#     response_format: type[T],
#     client: OpenAIClient | None = None,
#     **params: Unpack[OpenAIParams],
# ) -> StructuredAgentDecorator[DepsT, T]:
#     """Overload for OpenAI agents with response format."""
#     ...


@overload
def agent(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] = NoneType,
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: None = None,
    # client: Client | None = None,
    # **params: Unpack[Params],
) -> AgentDecorator[DepsT, None]:
    """Overload for all registered models so that autocomplete works."""
    ...


@overload
def agent(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] = NoneType,
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[FormatT],
    # client: Client | None = None,
    # **params: Unpack[Params],
) -> AgentDecorator[DepsT, FormatT]:
    """Overload for all registered models so that autocomplete works."""
    ...


def agent(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] = NoneType,
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[FormatT] | None = None,
    # client: Client | None = None,
    # **params: Unpack[Params],
) -> AgentDecorator[DepsT, None] | AgentDecorator[DepsT, FormatT]:
    """Decorator for creating an agent or structured agent.

    Args:
        model: The model to use for the agent.
        deps_type: The type of dependencies for the agent, injected into the context.
        tools: The tools available to the agent.
        response_format: The response format type for the agent.
        client: The client to use for the agent.
        **params: Additional parameters for the model.

    Returns:
        An instance of `AgentDecorator` or `StructuredAgentDecorator`.
    """
    raise NotImplementedError()
