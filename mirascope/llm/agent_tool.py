"""The `AgentTool` class."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any, Generic, ParamSpec, Protocol, TypeVar, overload

from pydantic.json_schema import SkipJsonSchema

from ..core import FromCallArgs
from .agent_context import AgentContext
from .tool import Tool

_P = ParamSpec("_P")

_AgentContextT = TypeVar("_AgentContextT", bound=AgentContext)
_ContravariantAgentContextT = TypeVar(
    "_ContravariantAgentContextT", contravariant=True, bound=AgentContext
)


class AgentTool(Tool, Generic[_AgentContextT]):
    """An `AgentTool` is just a `Tool` generic on the agent's context type.

    This is so that we can enforce that tools used in an `llm.agent` call are properly
    typed and have access to the context.

    We need to remove the context argument from the tool call signature so that we can
    use `tool.call()` as normal except that the context will be injected under the hood.
    """

    context: Annotated[SkipJsonSchema[_AgentContextT], FromCallArgs()]


class AgentToolFunction(Protocol[_ContravariantAgentContextT]):
    """Protocol for functions that can be used as agent tools.

    This protocol requires that the function has a context parameter.
    """

    def __call__(
        self,
        context: _ContravariantAgentContextT,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> Any: ...  # noqa: ANN401


@overload
def tool(*, context_type: None = None) -> Callable[[Callable[_P, Any]], type[Tool]]: ...


@overload
def tool(
    *, context_type: type[_AgentContextT]
) -> Callable[[AgentToolFunction[_AgentContextT]], type[AgentTool[_AgentContextT]]]: ...


def tool(
    *, context_type: type[_AgentContextT] | None = None
) -> (
    Callable[[Callable[_P, Any]], type[Tool]]
    | Callable[[AgentToolFunction[_AgentContextT]], type[AgentTool[_AgentContextT]]]
):
    """Decorator for turning a function into a `Tool` or `AgentTool`."""
    if not context_type:

        def tool_decorator(fn: Callable[_P, Any]) -> type[Tool]:
            return Tool.type_from_fn(fn)

        return tool_decorator

    def agent_tool_decorator(
        fn: AgentToolFunction[_AgentContextT],
    ) -> type[AgentTool[_AgentContextT]]:
        return AgentTool[_AgentContextT].type_from_fn(fn, exclude={"context"})

    return agent_tool_decorator
