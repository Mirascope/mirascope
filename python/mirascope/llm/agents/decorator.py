"""The `llm.agent` decorator for turning a function into an agent."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, overload

from typing_extensions import Unpack

from ..prompts import (
    AsyncContextSystemPrompt,
    AsyncSystemPrompt,
    ContextSystemPrompt,
    SystemPrompt,
)
from ..tools import AgentToolT, AsyncContextTool, AsyncTool, ContextTool, Tool
from .agent_template import AgentTemplate, AsyncAgentTemplate

if TYPE_CHECKING:
    from ..clients import (
        AnthropicClient,
        AnthropicModel,
        AnthropicParams,
        BaseClient,
        BaseParams,
        GoogleClient,
        GoogleModel,
        GoogleParams,
        Model,
        OpenAIClient,
        OpenAIModel,
        OpenAIParams,
        Provider,
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
            None | Tool | ContextTool[DepsT, ...],
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
            None | AsyncTool | AsyncContextTool[DepsT, ...],
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
        raise NotImplementedError()


@overload
def agent(
    *,
    provider: Literal["anthropic"],
    model: AnthropicModel,
    tools: list[AgentToolT] | None = None,
    format: type[FormatT] | None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> AgentDecorator[..., AgentToolT, FormatT]:
    """Decorator for creating an Anthropic agent."""
    ...


@overload
def agent(
    *,
    provider: Literal["google"],
    model: GoogleModel,
    tools: list[AgentToolT] | None = None,
    format: type[FormatT] | None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> AgentDecorator[..., AgentToolT, FormatT]:
    """Decorator for creating a Google agent."""
    ...


@overload
def agent(
    *,
    provider: Literal["openai"],
    model: OpenAIModel,
    tools: list[AgentToolT] | None = None,
    format: type[FormatT] | None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> AgentDecorator[..., AgentToolT, FormatT]:
    """Decorator for creating an OpenAI agent."""
    ...


@overload
def agent(
    *,
    provider: Provider,
    model: Model,
    tools: list[AgentToolT] | None = None,
    format: type[FormatT] | None = None,
    client: None = None,
    **params: Unpack[BaseParams],
) -> AgentDecorator[..., AgentToolT, FormatT]:
    """Decorator for creating an agent using any registered model."""
    ...


def agent(
    *,
    provider: Provider,
    model: Model,
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
