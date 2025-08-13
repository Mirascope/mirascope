"""The `ContextTool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Concatenate, Generic

from typing_extensions import TypeVar

from ..content import ToolCall, ToolOutput
from ..context import Context, DepsT
from ..types import Jsonable, JsonableCovariantT, P
from .tool import AsyncTool, Tool
from .tool_schema import ToolSchema

ContextToolT = TypeVar(
    "ContextToolT",
    bound=Tool[..., Jsonable]
    | "ContextTool[..., Jsonable, Any]"
    | AsyncTool[..., Jsonable]
    | "AsyncContextTool[..., Jsonable, Any]",
    covariant=True,
)
AgentToolT = TypeVar(
    "AgentToolT",
    bound=Tool[..., Jsonable]
    | "ContextTool[..., Jsonable, Any]"
    | AsyncTool[..., Jsonable]
    | "AsyncContextTool[..., Jsonable, Any]"
    | None,
    covariant=True,
    default=None,
)


@dataclass
class ContextTool(
    ToolSchema[Callable[Concatenate[Context[DepsT], P], JsonableCovariantT]],
    Generic[P, JsonableCovariantT, DepsT],
):
    """Protocol defining a tool that can be used by LLMs.

    A `ContextTool` represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> JsonableCovariantT:
        raise NotImplementedError()

    def execute(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> ToolOutput[JsonableCovariantT]:
        """Call the tool using an LLM-provided `ToolCall`."""
        raise NotImplementedError()


@dataclass
class AsyncContextTool(
    ToolSchema[Callable[Concatenate[Context[DepsT], P], JsonableCovariantT]],
    Generic[P, JsonableCovariantT, DepsT],
):
    """Protocol defining an async tool that can be used by LLMs with context.

    An `AsyncContextTool` represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Awaitable[JsonableCovariantT]:
        raise NotImplementedError()

    async def execute(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> ToolOutput[JsonableCovariantT]:
        """Call the tool using an LLM-provided `ToolCall`."""
        raise NotImplementedError()
