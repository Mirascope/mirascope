"""The `llm.agent` decorator for turning a function into an agent."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, overload

from typing_extensions import Unpack

from ..clients import BaseClient, BaseParams
from ..prompts import (
    AsyncContextSystemPrompt,
    AsyncSystemPrompt,
    ContextSystemPrompt,
    SystemPrompt,
)
from ..tools import AgentToolT, AsyncContextTool, AsyncTool, ContextTool, Tool
from ..types import Jsonable
from .agent_template import AgentTemplate, AsyncAgentTemplate

if TYPE_CHECKING:
    from ..clients import (
        REGISTERED_LLMS,
    )

from ..context import DepsT
from ..formatting import FormatT
from ..types import P

NoneType = type(None)


class AgentDecorator(Protocol[P, AgentToolT, FormatT]):
    """Protocol for the `agent` decorator."""

    @overload
    def __call__(
        self: AgentDecorator[
            P,
            None
            | Tool[..., Jsonable]
            | ContextTool[..., Jsonable, DepsT]
            | AsyncTool[..., Jsonable]
            | AsyncContextTool[..., Jsonable, DepsT],
            FormatT,
        ],
        fn: SystemPrompt[P] | ContextSystemPrompt[P, DepsT],
    ) -> AgentTemplate[DepsT, FormatT]:
        """Decorator for creating a sync agent."""
        ...

    @overload
    def __call__(
        self: AgentDecorator[
            P,
            None
            | Tool[..., Jsonable]
            | ContextTool[..., Jsonable, DepsT]
            | AsyncTool[..., Jsonable]
            | AsyncContextTool[..., Jsonable, DepsT],
            FormatT,
        ],
        fn: AsyncSystemPrompt[P] | AsyncContextSystemPrompt[P, DepsT],
    ) -> AsyncAgentTemplate[DepsT, FormatT]:
        """Decorator for creating an async agent."""
        ...

    def __call__(
        self,
        fn: SystemPrompt[P]
        | ContextSystemPrompt[P, DepsT]
        | AsyncSystemPrompt[P]
        | AsyncContextSystemPrompt[P, DepsT],
    ) -> AgentTemplate[DepsT, FormatT] | AsyncAgentTemplate[DepsT, FormatT]:
        """Decorator for creating an agent."""
        ...


# @overload
# def agent(
#     model: ANTHROPIC_REGISTERED_LLMS,
#     *,
#     tools: None = None,
#     format: type[FormatT] | None = None,
#     client: AnthropicClient | None = None,
#     **params: Unpack[AnthropicParams],
# ) -> AgentDecorator[None, DepsT, FormatT]:
#     """Overload for Anthropic agents with no tools."""
#     ...


# @overload
# def agent(
#     model: ANTHROPIC_REGISTERED_LLMS,
#     *,
#     tools: list[AgentToolT],
#     format: type[FormatT] | None = None,
#     client: AnthropicClient | None = None,
#     **params: Unpack[AnthropicParams],
# ) -> AgentDecorator[AgentToolT, DepsT, FormatT]:
#     """Overload for Anthropic agents with tools."""
#     ...


# @overload
# def agent(
#     model: GOOGLE_REGISTERED_LLMS,
#     *,
#     tools: None = None,
#     format: type[FormatT] | None = None,
#     client: GoogleClient | None = None,
#     **params: Unpack[GoogleParams],
# ) -> AgentDecorator[None, DepsT, FormatT]:
#     """Overload for Google agents with no tools."""
#     ...


# @overload
# def agent(
#     model: GOOGLE_REGISTERED_LLMS,
#     *,
#     tools: list[AgentToolT],
#     format: type[FormatT] | None = None,
#     client: GoogleClient | None = None,
#     **params: Unpack[GoogleParams],
# ) -> AgentDecorator[AgentToolT, DepsT, FormatT]:
#     """Overload for Google agents with tools."""
#     ...


# @overload
# def agent(
#     model: OPENAI_REGISTERED_LLMS,
#     *,
#     tools: None = None,
#     format: type[FormatT] | None = None,
#     client: OpenAIClient | None = None,
#     **params: Unpack[OpenAIParams],
# ) -> AgentDecorator[None, DepsT, FormatT]:
#     """Overload for OpenAI agents with no tools."""
#     ...


# @overload
# def agent(
#     model: OPENAI_REGISTERED_LLMS,
#     *,
#     tools: list[AgentToolT],
#     format: type[FormatT] | None = None,
#     client: OpenAIClient | None = None,
#     **params: Unpack[OpenAIParams],
# ) -> AgentDecorator[AgentToolT, DepsT, FormatT]:
#     """Overload for OpenAI agents with tools."""
#     ...


def agent(
    model: REGISTERED_LLMS,
    *,
    tools: list[AgentToolT] | None = None,
    format: type[FormatT] | None = None,
    client: BaseClient | None = None,
    **params: Unpack[BaseParams],
) -> AgentDecorator[..., AgentToolT, FormatT]:
    """Decorator for creating an agent or structured agent.

    Args:
        model: The model to use for the agent.
        tools: The tools available to the agent.
        format: The response format type for the agent.
        client: The client to use for the agent.
        **params: Additional parameters for the model.

    Returns:
        An of `AgentDecorator`.
    """
    raise NotImplementedError()
