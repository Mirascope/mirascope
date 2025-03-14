"""The `AgentTool` Class and `tool` Decorator."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, ParamSpec, Protocol, TypeVar, overload

from ...llm.tool import Tool
from .agent_context import AgentContext

_P = ParamSpec("_P")

_DepsT = TypeVar("_DepsT")


class AgentTool(Tool, Generic[_DepsT]):
    """An `AgentTool` is just a `Tool` generic on the agent's context type.

    This is so that we can enforce that tools used in an `llm.agent` call are properly
    typed and have access to the context.

    We need to remove the context argument from the tool call signature so that we can
    use `tool.call()` as normal except that the context will be injected under the hood.
    """


class AgentToolFunction(Protocol[_P, _DepsT]):
    """Protocol for functions that can be used as agent tools.

    This protocol requires that the function has a context parameter.
    """

    def __call__(
        self,
        ctx: AgentContext[_DepsT],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> Any: ...  # noqa: ANN401


@overload
def tool(*, deps_type: None = None) -> Callable[[Callable[_P, Any]], type[Tool]]: ...


@overload
def tool(
    *, deps_type: type[_DepsT]
) -> Callable[[AgentToolFunction[_P, _DepsT]], type[AgentTool[_DepsT]]]: ...


def tool(
    *, deps_type: type[_DepsT] | None = None
) -> (
    Callable[[Callable[_P, Any]], type[Tool]]
    | Callable[[AgentToolFunction[_P, _DepsT]], type[AgentTool[_DepsT]]]
):
    """Decorator for turning a function into a `Tool` or `AgentTool`."""
    if not deps_type:

        def tool_decorator(fn: Callable[_P, Any]) -> type[Tool]:
            return Tool.type_from_fn(fn)

        return tool_decorator

    def agent_tool_decorator(
        fn: AgentToolFunction[_P, _DepsT],
    ) -> type[AgentTool[_DepsT]]:
        return AgentTool[_DepsT].type_from_fn(fn)

    return agent_tool_decorator
