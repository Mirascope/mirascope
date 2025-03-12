"""Tool class for the provider-agnostic tool."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any, Generic, ParamSpec, Protocol, TypeVar, overload

from pydantic._internal._model_construction import ModelMetaclass
from pydantic.json_schema import SkipJsonSchema

from ..core import FromCallArgs
from ..core.base.tool import BaseTool
from .agent_context import AgentContext

_P = ParamSpec("_P")

_DepsT = TypeVar("_DepsT")


class _DelegateAbstractMethodsForTool(ModelMetaclass):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,  # noqa: ANN401
    ) -> type:
        cls = super().__new__(mcls, name, bases, namespace)
        cls.__abstractmethods__ = frozenset()
        return cls


class Tool(BaseTool, metaclass=_DelegateAbstractMethodsForTool):
    """
    A provider-agnostic Tool class.
    - No BaseProviderConverter
    - Relies on _response having `common_` methods/properties if needed.
    """

    _tool: BaseTool

    def __init__(self, tool: BaseTool) -> None:
        super().__init__(**{field: getattr(tool, field) for field in tool.model_fields})
        object.__setattr__(self, "_tool", tool)

    def __getattribute__(self, name: str) -> Any:  # noqa: ANN401
        special_names = {
            "_response",
            "__dict__",
            "__class__",
            "model_fields",
            "__annotations__",
            "__pydantic_validator__",
            "__pydantic_fields_set__",
            "__pydantic_extra__",
            "__pydantic_private__",
            "__class_getitem__",
        }

        if name in special_names:
            return object.__getattribute__(self, name)

        try:
            tool = object.__getattribute__(self, "_tool")
            return getattr(tool, name)
        except AttributeError:
            return object.__getattribute__(self, name)


class AgentTool(Tool, Generic[_DepsT]):
    """An `AgentTool` is just a `Tool` generic on the agent's context type.

    This is so that we can enforce that tools used in an `llm.agent` call are properly
    typed and have access to the context.

    We need to remove the context argument from the tool call signature so that we can
    use `tool.call()` as normal except that the context will be injected under the hood.
    """

    context: Annotated[SkipJsonSchema[AgentContext[_DepsT]], FromCallArgs()]


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
        return AgentTool[_DepsT].type_from_fn(fn, exclude={"context"})

    return agent_tool_decorator
