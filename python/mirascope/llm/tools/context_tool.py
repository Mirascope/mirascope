"""The `ContextTool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

from collections.abc import Awaitable
from typing import Any, Generic

from typing_extensions import TypeVar

from ..content import ToolCall, ToolOutput
from ..context import Context, DepsT
from ..types import AnyP, JsonableCovariantT
from .protocols import AsyncContextToolFn, ContextToolFn
from .tool import AsyncTool, Tool
from .tool_schema import ToolSchema

ContextToolT = TypeVar(
    "ContextToolT",
    bound="Tool | AsyncTool | ContextTool[Any] | AsyncContextTool[Any]",
    covariant=True,
)
AgentToolT = TypeVar(
    "AgentToolT",
    bound="Tool | AsyncTool | ContextTool[Any] | AsyncContextTool[Any] | None",
    covariant=True,
    default=None,
)


class ContextTool(
    ToolSchema[ContextToolFn[DepsT, AnyP, JsonableCovariantT]],
    Generic[DepsT, AnyP, JsonableCovariantT],
):
    """Protocol defining a tool that can be used by LLMs.

    A `ContextTool` represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __call__(
        self,
        ctx: Context[DepsT],
        *args: AnyP.args,
        **kwargs: AnyP.kwargs,
    ) -> JsonableCovariantT:
        raise NotImplementedError()

    def execute(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> ToolOutput[JsonableCovariantT]:
        """Call the tool using an LLM-provided `ToolCall`."""
        raise NotImplementedError()


class AsyncContextTool(
    ToolSchema[AsyncContextToolFn[DepsT, AnyP, JsonableCovariantT]],
    Generic[DepsT, AnyP, JsonableCovariantT],
):
    """Protocol defining an async tool that can be used by LLMs with context.

    An `AsyncContextTool` represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __call__(
        self,
        ctx: Context[DepsT],
        *args: AnyP.args,
        **kwargs: AnyP.kwargs,
    ) -> Awaitable[JsonableCovariantT]:
        raise NotImplementedError()

    async def execute(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> ToolOutput[JsonableCovariantT]:
        """Call the tool using an LLM-provided `ToolCall`."""
        raise NotImplementedError()
