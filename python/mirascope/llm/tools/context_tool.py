"""The `ContextTool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

import json
from collections.abc import Awaitable
from typing import Any, Generic, Protocol, cast

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


class _KwargContextCallable(Protocol[DepsT, JsonableCovariantT]):
    def __call__(
        self, ctx: Context[DepsT], /, **kwargs: dict[str, Any]
    ) -> JsonableCovariantT: ...


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
        """Call the underlying function directly with context."""
        return self.fn(ctx, *args, **kwargs)

    def execute(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> ToolOutput[JsonableCovariantT]:
        """Execute the context tool using an LLM-provided `ToolCall`."""
        kwargs = json.loads(tool_call.args)
        result = cast(_KwargContextCallable[DepsT, JsonableCovariantT], self.fn)(
            ctx, **kwargs
        )
        return ToolOutput(id=tool_call.id, value=result, name=self.name)


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
        """Call the underlying async function directly with context."""
        return self.fn(ctx, *args, **kwargs)

    async def execute(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> ToolOutput[JsonableCovariantT]:
        """Execute the async context tool using an LLM-provided `ToolCall`."""
        args = json.loads(tool_call.args)
        result = await self.fn(ctx, **args)  # type: ignore[reportCallIssue]
        return ToolOutput(id=tool_call.id, value=result, name=self.name)
