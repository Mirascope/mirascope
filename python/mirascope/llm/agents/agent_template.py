from typing import Generic, overload

from ..context import DepsT
from ..formatting import FormatT
from .agent import Agent, AsyncAgent


class AgentTemplate(Generic[DepsT, FormatT]):
    @overload
    def __call__(self: "AgentTemplate[None, FormatT]") -> Agent[None, FormatT]:
        """Create an Agent with no deps"""

    @overload
    def __call__(
        self: "AgentTemplate[DepsT, FormatT]", deps: DepsT
    ) -> Agent[DepsT, FormatT]:
        """Create an Agent with deps"""

    def __call__(
        self: "AgentTemplate[None, FormatT]" | "AgentTemplate[DepsT, FormatT]",
        deps: DepsT | None = None,
    ) -> Agent[None, FormatT] | Agent[DepsT, FormatT]:
        raise NotImplementedError()


class AsyncAgentTemplate(Generic[DepsT, FormatT]):
    @overload
    async def __call__(
        self: "AsyncAgentTemplate[None, FormatT]",
    ) -> AsyncAgent[None, FormatT]:
        """Create an AsyncAgent with no deps"""

    @overload
    async def __call__(
        self: "AsyncAgentTemplate[DepsT, FormatT]", deps: DepsT
    ) -> AsyncAgent[DepsT, FormatT]:
        """Create an AsyncAgent with deps"""

    async def __call__(
        self: "AsyncAgentTemplate[None, FormatT]"
        | "AsyncAgentTemplate[DepsT, FormatT]",
        deps: DepsT | None = None,
    ) -> AsyncAgent[None, FormatT] | AsyncAgent[DepsT, FormatT]:
        raise NotImplementedError()
