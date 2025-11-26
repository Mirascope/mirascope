"""The `llm.agent` decorator for turning a function into an agent."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Protocol, overload
from typing_extensions import TypeVar, Unpack

from ..tools import AsyncContextTool, AsyncTool, ContextTool, Tool
from .agent_template import AgentTemplate, AsyncAgentTemplate

if TYPE_CHECKING:
    from ..clients import (
        AnthropicClient,
        AnthropicModelId,
        BaseClient,
        GoogleClient,
        GoogleModelId,
        ModelId,
        OpenAICompletionsClient,
        OpenAICompletionsModelId,
        Params,
        Provider,
    )

from ..context import Context, DepsT
from ..formatting import FormattableT
from ..types import P

AgentToolT = TypeVar(
    "AgentToolT",
    bound="Tool | AsyncTool | ContextTool[Any] | AsyncContextTool[Any] | None",
    covariant=True,
    default=None,
)


class SystemPrompt(Protocol[P]):
    """Protocol for a prompt template function that returns a system prompt as a string (no context)."""

    def __call__(self) -> str: ...


class ContextSystemPrompt(Protocol[P, DepsT]):
    """Protocol for a prompt template function that returns a system prompt as a string (with context)."""

    def __call__(self, ctx: Context[DepsT]) -> str: ...


class AsyncSystemPrompt(Protocol[P]):
    """Protocol for an async prompt template function that returns a system prompt as a string (no context)."""

    async def __call__(self) -> str: ...


class AsyncContextSystemPrompt(Protocol[P, DepsT]):
    """Protocol for an async prompt template function that returns a system prompt as a string (with context)."""

    async def __call__(self, ctx: Context[DepsT]) -> str: ...


class AgentDecorator(Protocol[P, AgentToolT, FormattableT]):
    """Protocol for the `agent` decorator."""

    @overload
    def __call__(
        self: AgentDecorator[
            P,
            None | Tool | ContextTool[DepsT],
            FormattableT,
        ],
        fn: SystemPrompt[P] | ContextSystemPrompt[P, DepsT],
    ) -> AgentTemplate[DepsT, FormattableT]:
        """Decorator for creating a sync agent."""
        ...

    @overload
    def __call__(
        self: AgentDecorator[
            P,
            None | AsyncTool | AsyncContextTool[DepsT],
            FormattableT,
        ],
        fn: AsyncSystemPrompt[P] | AsyncContextSystemPrompt[P, DepsT],
    ) -> AsyncAgentTemplate[DepsT, FormattableT]:
        """Decorator for creating an async agent."""
        ...

    def __call__(
        self,
        fn: SystemPrompt[P]
        | ContextSystemPrompt[P, DepsT]
        | AsyncSystemPrompt[P]
        | AsyncContextSystemPrompt[P, DepsT],
    ) -> AgentTemplate[DepsT, FormattableT] | AsyncAgentTemplate[DepsT, FormattableT]:
        """Decorator for creating an agent."""
        raise NotImplementedError()


@overload
def agent(
    *,
    provider: Literal["anthropic"],
    model_id: AnthropicModelId,
    tools: list[AgentToolT] | None = None,
    format: type[FormattableT] | None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[Params],
) -> AgentDecorator[..., AgentToolT, FormattableT]:
    """Decorator for creating an Anthropic agent."""
    ...


@overload
def agent(
    *,
    provider: Literal["google"],
    model_id: GoogleModelId,
    tools: list[AgentToolT] | None = None,
    format: type[FormattableT] | None = None,
    client: GoogleClient | None = None,
    **params: Unpack[Params],
) -> AgentDecorator[..., AgentToolT, FormattableT]:
    """Decorator for creating a Google agent."""
    ...


@overload
def agent(
    *,
    provider: Literal["openai:completions"],
    model_id: OpenAICompletionsModelId,
    tools: list[AgentToolT] | None = None,
    format: type[FormattableT] | None = None,
    client: OpenAICompletionsClient | None = None,
    **params: Unpack[Params],
) -> AgentDecorator[..., AgentToolT, FormattableT]:
    """Decorator for creating an OpenAI agent."""
    ...


@overload
def agent(
    *,
    provider: Provider,
    model_id: ModelId,
    tools: list[AgentToolT] | None = None,
    format: type[FormattableT] | None = None,
    client: None = None,
    **params: Unpack[Params],
) -> AgentDecorator[..., AgentToolT, FormattableT]:
    """Decorator for creating an agent using any registered model."""
    ...


def agent(
    *,
    provider: Provider,
    model_id: ModelId,
    tools: list[AgentToolT] | None = None,
    format: type[FormattableT] | None = None,
    client: BaseClient[str, Any, Any] | None = None,
    **params: Unpack[Params],
) -> AgentDecorator[..., AgentToolT, FormattableT]:
    """Decorator for creating an agent or structured agent.

    Args:
        model_id: The model to use for the agent.
        tools: The tools available to the agent.
        format: The response format type for the agent.
        client: The client to use for the agent.
        **params: Additional parameters for the model.

    Returns:
        An of `AgentDecorator`.
    """
    raise NotImplementedError()
