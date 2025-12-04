"""The `Tool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

import json
from collections.abc import Awaitable
from typing import Any, Generic, cast
from typing_extensions import TypeVar

from ..content import ToolCall, ToolOutput
from ..context import Context, DepsT
from ..types import AnyP, JsonableCovariantT
from .protocols import (
    AsyncContextToolFn,
    AsyncJsonKwargsCallable,
    AsyncKwargsCallable,
    AsyncToolFn,
    ContextKwargsCallable,
    ContextToolFn,
    KwargsCallable,
    ToolFn,
)
from .tool_schema import ToolSchema

ToolT = TypeVar(
    "ToolT",
    bound="Tool | AsyncTool | ContextTool[Any] | AsyncContextTool[Any]",
    covariant=True,
)


class Tool(
    ToolSchema[ToolFn[AnyP, JsonableCovariantT]], Generic[AnyP, JsonableCovariantT]
):
    """A tool that can be used by LLMs.

    A `Tool` represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __init__(
        self, fn: ToolFn[AnyP, JsonableCovariantT], *, strict: bool = False
    ) -> None:
        super().__init__(fn, strict=strict, is_context_tool=False)

    def __call__(self, *args: AnyP.args, **kwargs: AnyP.kwargs) -> JsonableCovariantT:
        """Call the underlying function directly."""
        return self.fn(*args, **kwargs)

    def execute(self, tool_call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Execute the tool using an LLM-provided `ToolCall`."""
        kwargs_from_json = json.loads(tool_call.args)
        kwargs_callable = cast(KwargsCallable[JsonableCovariantT], self.fn)
        result = kwargs_callable(**kwargs_from_json)
        return ToolOutput(id=tool_call.id, value=result, name=self.name)


class AsyncTool(
    ToolSchema[AsyncToolFn[AnyP, JsonableCovariantT]],
    Generic[AnyP, JsonableCovariantT],
):
    """An async tool that can be used by LLMs.

    An `AsyncTool` represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __init__(
        self, fn: AsyncToolFn[AnyP, JsonableCovariantT], *, strict: bool = False
    ) -> None:
        super().__init__(fn, strict=strict, is_context_tool=False)

    def __call__(
        self, *args: AnyP.args, **kwargs: AnyP.kwargs
    ) -> Awaitable[JsonableCovariantT]:
        """Call the underlying async function directly."""
        return self.fn(*args, **kwargs)

    async def execute(self, tool_call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Execute the async tool using an LLM-provided `ToolCall`."""
        kwargs_from_json = json.loads(tool_call.args)
        kwargs_callable = cast(AsyncKwargsCallable[JsonableCovariantT], self.fn)
        result = await kwargs_callable(**kwargs_from_json)
        return ToolOutput(id=tool_call.id, value=result, name=self.name)


class ContextTool(
    ToolSchema[ContextToolFn[DepsT, AnyP, JsonableCovariantT]],
    Generic[DepsT, JsonableCovariantT, AnyP],
):
    """Protocol defining a tool that can be used by LLMs.

    A `ContextTool` represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __init__(
        self,
        fn: ContextToolFn[DepsT, AnyP, JsonableCovariantT],
        *,
        strict: bool = False,
    ) -> None:
        super().__init__(fn, strict=strict, is_context_tool=True)

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
        kwargs_from_json = json.loads(tool_call.args)
        kwargs_callable = cast(
            ContextKwargsCallable[DepsT, JsonableCovariantT], self.fn
        )
        result = kwargs_callable(ctx, **kwargs_from_json)
        return ToolOutput(id=tool_call.id, value=result, name=self.name)


class AsyncContextTool(
    ToolSchema[AsyncContextToolFn[DepsT, AnyP, JsonableCovariantT]],
    Generic[DepsT, JsonableCovariantT, AnyP],
):
    """Protocol defining an async tool that can be used by LLMs with context.

    An `AsyncContextTool` represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __init__(
        self,
        fn: AsyncContextToolFn[DepsT, AnyP, JsonableCovariantT],
        *,
        strict: bool = False,
    ) -> None:
        super().__init__(fn, strict=strict, is_context_tool=True)

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
        kwargs_from_json = json.loads(tool_call.args)
        kwargs_callable = cast(
            AsyncJsonKwargsCallable[DepsT, JsonableCovariantT], self.fn
        )
        result = await kwargs_callable(ctx, **kwargs_from_json)
        return ToolOutput(id=tool_call.id, value=result, name=self.name)
