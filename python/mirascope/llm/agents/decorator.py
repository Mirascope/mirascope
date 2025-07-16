"""The `llm.agent` decorator for turning a function into an agent."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, overload

from typing_extensions import Unpack

from ..clients import BaseClient, BaseParams
from ..context import Context
from ..tools import (
    AgentToolT,
    ContextTool,
    Tool,
)
from ..types import Jsonable
from .agent import Agent
from .async_agent import AsyncAgent

if TYPE_CHECKING:
    from ..clients import (
        ANTHROPIC_REGISTERED_LLMS,
        GOOGLE_REGISTERED_LLMS,
        OPENAI_REGISTERED_LLMS,
        REGISTERED_LLMS,
        AnthropicClient,
        AnthropicParams,
        GoogleClient,
        GoogleParams,
        OpenAIClient,
        OpenAIParams,
    )

from ..context import DepsT
from ..response_formatting import FormatT
from ..types import P

NoneType = type(None)


class SystemPrompt(Protocol[P, DepsT]):
    """Protocol for a prompt template function that returns a system prompt as a string."""

    def __call__(self, ctx: Context[DepsT]) -> str: ...


class AsyncSystemPrompt(Protocol[P, DepsT]):
    """Protocol for an async prompt template function that returns a system prompt as a string."""

    async def __call__(self, ctx: Context[DepsT]) -> str: ...


class AgentDecorator(Protocol[AgentToolT, DepsT, FormatT]):
    """Protocol for the `agent` decorator."""

    @overload
    def __call__(
        self: AgentDecorator[None, DepsT, FormatT],
        fn: SystemPrompt[P, DepsT],
    ) -> Agent[DepsT, FormatT]:
        """Decorator for creating a sync agent with no tools."""
        ...

    @overload
    def __call__(
        self: AgentDecorator[
            Tool[..., Jsonable] | ContextTool[..., Jsonable, DepsT], DepsT, FormatT
        ],
        fn: SystemPrompt[P, DepsT],
    ) -> Agent[DepsT, FormatT]:
        """Decorator for creating an sync agent with sync tools."""
        ...

    @overload
    def __call__(
        self,
        fn: AsyncSystemPrompt[P, DepsT],
    ) -> AsyncAgent[DepsT, FormatT]:
        """Decorator for creating an async only agent with async prompt."""
        ...

    @overload
    def __call__(
        self,
        fn: SystemPrompt[P, DepsT],
    ) -> AsyncAgent[DepsT, FormatT]:
        """Decorator for creating an async agent from sync function with async tools."""
        ...

    def __call__(
        self, fn: SystemPrompt[P, DepsT] | AsyncSystemPrompt[P, DepsT]
    ) -> Agent[DepsT, FormatT] | AsyncAgent[DepsT, FormatT]:
        """Decorator for creating an agent."""
        ...


class AsyncAgentDecorator(Protocol[DepsT, FormatT]):
    """Protocol for the `agent` decorator with async tools."""

    @overload
    def __call__(self, fn: AsyncSystemPrompt[P, DepsT]) -> AsyncAgent[DepsT, FormatT]:
        """Decorator for creating an async only agent."""
        ...

    @overload
    def __call__(self, fn: SystemPrompt[P, DepsT]) -> AsyncAgent[DepsT, FormatT]:
        """Decorator for creating an async agent from sync function."""
        ...

    def __call__(
        self, fn: SystemPrompt[P, DepsT] | AsyncSystemPrompt[P, DepsT]
    ) -> AsyncAgent[DepsT, FormatT]:
        """Decorator for creating an async agent."""
        ...


@overload
def agent(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    tools: None = None,
    deps_type: type[DepsT] = NoneType,
    response_format: type[FormatT] | None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> AgentDecorator[None, DepsT, FormatT]:
    """Overload for Anthropic agents with no tools."""
    ...


@overload
def agent(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    tools: list[AgentToolT],
    deps_type: type[DepsT] = NoneType,
    response_format: type[FormatT] | None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> AgentDecorator[AgentToolT, DepsT, FormatT]:
    """Overload for Anthropic agents with tools."""
    ...


@overload
def agent(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    tools: None = None,
    deps_type: type[DepsT] = NoneType,
    response_format: type[FormatT] | None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> AgentDecorator[None, DepsT, FormatT]:
    """Overload for Google agents with no tools."""
    ...


@overload
def agent(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    tools: list[AgentToolT],
    deps_type: type[DepsT] = NoneType,
    response_format: type[FormatT] | None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> AgentDecorator[AgentToolT, DepsT, FormatT]:
    """Overload for Google agents with tools."""
    ...


@overload
def agent(
    model: OPENAI_REGISTERED_LLMS,
    *,
    tools: None = None,
    deps_type: type[DepsT] = NoneType,
    response_format: type[FormatT] | None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> AgentDecorator[None, DepsT, FormatT]:
    """Overload for OpenAI agents with no tools."""
    ...


@overload
def agent(
    model: OPENAI_REGISTERED_LLMS,
    *,
    tools: list[AgentToolT],
    deps_type: type[DepsT] = NoneType,
    response_format: type[FormatT] | None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> AgentDecorator[AgentToolT, DepsT, FormatT]:
    """Overload for OpenAI agents with tools."""
    ...


@overload
def agent(
    model: REGISTERED_LLMS,
    *,
    tools: None = None,
    deps_type: type[DepsT] = NoneType,
    response_format: type[FormatT] | None = None,
    client: BaseClient | None = None,
    **params: Unpack[BaseParams],
) -> AgentDecorator[None, DepsT, FormatT]:
    """Overload for agents with no tools."""
    ...


@overload
def agent(
    model: REGISTERED_LLMS,
    *,
    tools: list[AgentToolT],
    deps_type: type[DepsT] = NoneType,
    response_format: type[FormatT] | None = None,
    client: BaseClient | None = None,
    **params: Unpack[BaseParams],
) -> AgentDecorator[AgentToolT, DepsT, FormatT]:
    """Overload for agents with tools."""
    ...


def agent(
    model: REGISTERED_LLMS,
    *,
    tools: list[AgentToolT] | None = None,
    deps_type: type[DepsT] = NoneType,
    response_format: type[FormatT] | None = None,
    client: BaseClient | None = None,
    **params: Unpack[BaseParams],
) -> AgentDecorator[AgentToolT, DepsT, FormatT] | AgentDecorator[None, DepsT, FormatT]:
    """Decorator for creating an agent or structured agent.

    Args:
        model: The model to use for the agent.
        deps_type: The type of dependencies for the agent, injected into the context.
        tools: The tools available to the agent.
        response_format: The response format type for the agent.
        client: The client to use for the agent.
        **params: Additional parameters for the model.

    Returns:
        An instance of `AgentDecorator` or `AgentDecorator`.
    """
    raise NotImplementedError()
