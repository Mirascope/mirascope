"""The `ContextTool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Concatenate, Generic

from typing_extensions import TypeVar

from ..content import ToolCall, ToolOutput
from ..context import Context, DepsT
from ..types import Jsonable, JsonableCovariantT, P
from .base_tool import BaseTool
from .tool import AsyncTool, Tool

ContextToolT = TypeVar(
    "ContextToolT",
    bound=Tool[..., Jsonable]
    | "ContextTool[..., Jsonable, Any]"
    | AsyncTool[..., Jsonable]
    | "AsyncContextTool[..., Jsonable, Any]",
    covariant=True,
)
OptionalContextToolT = TypeVar(
    "OptionalContextToolT",
    bound=Tool[..., Jsonable]
    | "ContextTool[..., Jsonable, Any]"
    | AsyncTool[..., Jsonable]
    | "AsyncContextTool[..., Jsonable, Any]"
    | None,
    covariant=True,
    default=None,
)

ContravariantContextToolT = TypeVar(
    "ContravariantContextToolT",
    bound=Tool[..., Jsonable]
    | "ContextTool[..., Jsonable, Any]"
    | AsyncTool[..., Jsonable]
    | "AsyncContextTool[..., Jsonable, Any]"
    | None,
    contravariant=True,
    default=None,
)

InvariantContextToolT = TypeVar(
    "InvariantContextToolT",
    bound=Tool[..., Jsonable]
    | "ContextTool[..., Jsonable, Any]"
    | AsyncTool[..., Jsonable]
    | "AsyncContextTool[..., Jsonable, Any]"
    | None,
    default=None,
)


@dataclass
class ContextTool(
    BaseTool[P, JsonableCovariantT], Generic[P, JsonableCovariantT, DepsT]
):
    """Protocol defining a tool that can be used by LLMs.

    A Tool represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    fn: Callable[Concatenate[Context[DepsT], P], JsonableCovariantT]
    """The function that implements the tool's functionality."""

    def call(
        self, ctx: Context[DepsT], call: ToolCall
    ) -> ToolOutput[JsonableCovariantT]:
        """Call the tool using an LLM-provided ToolCall."""
        raise NotImplementedError()


@dataclass
class AsyncContextTool(
    BaseTool[P, JsonableCovariantT], Generic[P, JsonableCovariantT, DepsT]
):
    """Protocol defining an async tool that can be used by LLMs with context.

    An AsyncContextTool represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    fn: Callable[Concatenate[Context[DepsT], P], Awaitable[JsonableCovariantT]]
    """The async function that implements the tool's functionality."""

    async def call(
        self, ctx: Context[DepsT], call: ToolCall
    ) -> ToolOutput[JsonableCovariantT]:
        """Call the tool using an LLM-provided ToolCall."""
        raise NotImplementedError()
