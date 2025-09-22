from typing import Generic, overload

from ..context import DepsT
from ..formatting import FormattableT
from .agent import Agent, AsyncAgent


class AgentTemplate(Generic[DepsT, FormattableT]):
    @overload
    def __call__(
        self: "AgentTemplate[None, FormattableT]",
    ) -> Agent[None, FormattableT]:
        """Create an Agent with no deps"""

    @overload
    def __call__(
        self: "AgentTemplate[DepsT, FormattableT]", deps: DepsT
    ) -> Agent[DepsT, FormattableT]:
        """Create an Agent with deps"""

    def __call__(
        self: "AgentTemplate[None, FormattableT] | AgentTemplate[DepsT, FormattableT]",
        deps: DepsT | None = None,
    ) -> Agent[None, FormattableT] | Agent[DepsT, FormattableT]:
        raise NotImplementedError()


class AsyncAgentTemplate(Generic[DepsT, FormattableT]):
    @overload
    async def __call__(
        self: "AsyncAgentTemplate[None, FormattableT]",
    ) -> AsyncAgent[None, FormattableT]:
        """Create an AsyncAgent with no deps"""

    @overload
    async def __call__(
        self: "AsyncAgentTemplate[DepsT, FormattableT]", deps: DepsT
    ) -> AsyncAgent[DepsT, FormattableT]:
        """Create an AsyncAgent with deps"""

    async def __call__(
        self: "AsyncAgentTemplate[None, FormattableT] | AsyncAgentTemplate[DepsT, FormattableT]",
        deps: DepsT | None = None,
    ) -> AsyncAgent[None, FormattableT] | AsyncAgent[DepsT, FormattableT]:
        raise NotImplementedError()
