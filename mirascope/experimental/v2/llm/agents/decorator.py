"""The `llm.agent` decorator for turning a function into an agent."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ParamSpec, Protocol, TypeAlias, overload

from typing_extensions import TypeVar, Unpack

from ..content import Content
from ..context import Context
from ..models import Client, Params
from ..tools import ContextToolDef, ToolDef
from ..types import Dataclass
from .agent import Agent
from .async_agent import AsyncAgent
from .async_structured_agent import AsyncStructuredAgent
from .structured_agent import StructuredAgent

if TYPE_CHECKING:
    from ..models import (
        ANTHROPIC_REGISTERED_LLMS,
        GOOGLE_REGISTERED_LLMS,
        OPENAI_REGISTERED_LLMS,
        REGISTERED_LLMS,
    )
    from ..models.anthropic import AnthropicClient, AnthropicParams
    from ..models.google import GoogleClient, GoogleParams
    from ..models.openai import OpenAIClient, OpenAIParams

NoneType = type(None)
P = ParamSpec("P")
DepsT = TypeVar("DepsT", default=None)
T = TypeVar("T", bound=Dataclass | None, default=None)


class AgentStringReturn(Protocol[P, DepsT]):
    """Protocol for a prompt template function that returns a single string."""

    def __call__(self, ctx: Context[DepsT]) -> str: ...


class AsyncAgentStringReturn(Protocol[P, DepsT]):
    """Protocol for a prompt template function that returns a single string."""

    async def __call__(self, ctx: Context[DepsT]) -> str: ...


class AgentContentReturn(Protocol[P, DepsT]):
    """Protocol for a prompt template function that returns a single content part."""

    def __call__(self, ctx: Context[DepsT]) -> Content: ...


class AsyncAgentContentReturn(Protocol[P, DepsT]):
    """Protocol for a prompt template function that returns a single content part."""

    async def __call__(self, ctx: Context[DepsT]) -> Content: ...


class AgentContentSequenceReturn(Protocol[P, DepsT]):
    """Protocol for a prompt template function that returns a content parts sequence."""

    def __call__(self, ctx: Context[DepsT]) -> Sequence[Content]: ...


class AsyncAgentContentSequenceReturn(Protocol[P, DepsT]):
    """Protocol for a prompt template function that returns a content parts sequence."""

    async def __call__(self, ctx: Context[DepsT]) -> Sequence[Content]: ...


SystemPromptTemplate: TypeAlias = (
    AgentStringReturn[P, DepsT]
    | AgentContentReturn[P, DepsT]
    | AgentContentSequenceReturn[P, DepsT]
)
AsyncSystemPromptTemplate: TypeAlias = (
    AsyncAgentStringReturn[P, DepsT]
    | AsyncAgentContentReturn[P, DepsT]
    | AsyncAgentContentSequenceReturn[P, DepsT]
)


class AgentDecorator(Protocol[DepsT]):
    """Protocol for the `agent` decorator."""

    @overload
    def __call__(self, fn: AsyncSystemPromptTemplate[P, DepsT]) -> Agent[DepsT]:
        """Decorator for creating an async only agent."""
        ...

    @overload
    def __call__(self, fn: SystemPromptTemplate[P, DepsT]) -> Agent[DepsT]:
        """Decorator for creating an agent."""
        ...

    def __call__(
        self, fn: SystemPromptTemplate[P, DepsT] | AsyncSystemPromptTemplate[P, DepsT]
    ) -> Agent[DepsT] | AsyncAgent[DepsT]:
        """Decorator for creating an agent."""
        ...


class StructuredAgentDecorator(Protocol[DepsT, T]):
    """Protocol for the `agent` decorator with a response format."""

    @overload
    def __call__(
        self, fn: AsyncSystemPromptTemplate[P, DepsT]
    ) -> StructuredAgent[DepsT, T]:
        """Decorator for creating an async only structured agent."""
        ...

    @overload
    def __call__(self, fn: SystemPromptTemplate[P, DepsT]) -> StructuredAgent[DepsT, T]:
        """Decorator for creating a structured agent."""
        ...

    def __call__(
        self,
        fn: SystemPromptTemplate[P, DepsT] | AsyncSystemPromptTemplate[P, DepsT],
    ) -> StructuredAgent[DepsT, T] | AsyncStructuredAgent[DepsT, T]:
        """Decorator for creating a structured agent."""
        ...


@overload
def agent(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] = NoneType,
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> AgentDecorator[DepsT]:
    """Overload for Anthropic agents."""
    ...


@overload
def agent(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] = NoneType,
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[T],
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> StructuredAgentDecorator[DepsT, T]:
    """Overload for Anthropic agents with response format."""
    ...


@overload
def agent(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] = NoneType,
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> AgentDecorator[DepsT]:
    """Overload for Google agents."""
    ...


@overload
def agent(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] = NoneType,
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[T],
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> StructuredAgentDecorator[DepsT, T]:
    """Overload for Google agents with response format."""
    ...


@overload
def agent(
    model: OPENAI_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] = NoneType,
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> AgentDecorator[DepsT]:
    """Overload for OpenAI agents."""
    ...


@overload
def agent(
    model: OPENAI_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] = NoneType,
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[T],
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> StructuredAgentDecorator[DepsT, T]:
    """Overload for OpenAI agents with response format."""
    ...


@overload
def agent(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] = NoneType,
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[T] | None = None,
    client: Client | None = None,
    **params: Unpack[Params],
) -> AgentDecorator[DepsT] | StructuredAgentDecorator[DepsT, T]:
    """Overload for all registered models so that autocomplete works."""
    ...


def agent(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] = NoneType,
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[T] | None = None,
    client: Client | None = None,
    **params: Unpack[Params],
) -> AgentDecorator[DepsT] | StructuredAgentDecorator[DepsT, T]:
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
