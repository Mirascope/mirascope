"""The `AgentTool` Class and `tool` Decorator."""

from __future__ import annotations

from typing import Any, ParamSpec, Protocol, TypeVar

from .agent_context import AgentContext

_DepsT = TypeVar("_DepsT")


class AgentToolFunction(Protocol[_DepsT]):
    """Protocol for functions that can be used as agent tools.

    This protocol requires that the function has a context parameter.
    """

    def __call__(
        self,
        ctx: AgentContext[_DepsT],
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> Any: ...  # noqa: ANN401
