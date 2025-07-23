from collections.abc import Sequence
from typing import Generic, overload

from ..context import DepsT
from ..formatting import FormatT
from ..tools import ContextTool, ContextToolT, Tool
from ..types import Jsonable
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

    @overload
    def add_tools(  # type: ignore[reportOverlappingOverloads]
        self, tools: Sequence[Tool[..., Jsonable] | ContextTool[..., Jsonable, DepsT]]
    ) -> "AgentTemplate[DepsT, FormatT]":
        """Return AgentTemplate when tools are only sync."""
        ...

    @overload
    def add_tools(
        self, tools: Sequence[ContextToolT]
    ) -> "AsyncAgentTemplate[DepsT, FormatT]":
        """Return AsyncAgentTemplate when there are async tools."""
        ...

    def add_tools(
        self, tools: Sequence[ContextToolT]
    ) -> "AgentTemplate[DepsT, FormatT] | AsyncAgentTemplate[DepsT, FormatT]":
        """Creates a new AgentTemplate or AsyncAgentTemplate with additional tools.

        If tools contain any AsyncTool or AsyncContextTool, returns AsyncAgentTemplate.
        Otherwise returns AgentTemplate.
        """
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

    def add_tools(
        self, tools: Sequence[ContextToolT]
    ) -> "AsyncAgentTemplate[DepsT, FormatT]":
        """Creates a new AsyncAgentTemplate with additional tools."""
        raise NotImplementedError()
