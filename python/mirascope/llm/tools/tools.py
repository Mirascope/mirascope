"""The `Tool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

import json
from collections.abc import Awaitable
from typing import Any, Generic, cast
from typing_extensions import TypeVar

from ..content import ToolCall, ToolOutput
from ..context import Context, DepsT
from ..exceptions import ToolError, ToolExecutionError
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

    @classmethod
    def from_function(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls, fn: ToolFn[AnyP, JsonableCovariantT], *, strict: bool | None = None
    ) -> Tool[AnyP, JsonableCovariantT]:
        """Create a `Tool` by inspecting a function and its docstring.

        Args:
            fn: The function to extract schema from
            strict: Whether the tool should use strict mode when supported.
                If None, uses provider's default (usually as strict as possible).

        Returns:
            a `Tool` representing the function
        """
        schema = ToolSchema.from_function(fn, strict=strict, is_context_tool=False)
        return cls(
            fn=cast(ToolFn[AnyP, JsonableCovariantT], schema.fn),
            name=schema.name,
            description=schema.description,
            parameters=schema.parameters,
            strict=schema.strict,
        )

    def __call__(self, *args: AnyP.args, **kwargs: AnyP.kwargs) -> JsonableCovariantT:
        """Call the underlying function directly."""
        return self.fn(*args, **kwargs)

    def execute(self, tool_call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Execute the tool using an LLM-provided `ToolCall`."""
        kwargs_callable = cast(KwargsCallable[JsonableCovariantT], self.fn)
        error: ToolError | None = None
        try:
            kwargs_from_json = json.loads(tool_call.args)
            result = kwargs_callable(**kwargs_from_json)
        except Exception as e:
            result = str(e)
            error = ToolExecutionError(e)
        return ToolOutput(id=tool_call.id, result=result, error=error, name=self.name)


class AsyncTool(
    ToolSchema[AsyncToolFn[AnyP, JsonableCovariantT]],
    Generic[AnyP, JsonableCovariantT],
):
    """An async tool that can be used by LLMs.

    An `AsyncTool` represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    @classmethod
    def from_function(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls, fn: AsyncToolFn[AnyP, JsonableCovariantT], *, strict: bool | None = None
    ) -> AsyncTool[AnyP, JsonableCovariantT]:
        """Create an `AsyncTool` by inspecting a function and its docstring.

        Args:
            fn: The function to extract schema from
            strict: Whether the tool should use strict mode when supported.
                If None, uses provider's default (usually as strict as possible).

        Returns:
            an `AsyncTool` representing the function
        """
        schema = ToolSchema.from_function(fn, strict=strict, is_context_tool=False)
        return cls(
            fn=cast(AsyncToolFn[AnyP, JsonableCovariantT], schema.fn),
            name=schema.name,
            description=schema.description,
            parameters=schema.parameters,
            strict=schema.strict,
        )

    def __call__(
        self, *args: AnyP.args, **kwargs: AnyP.kwargs
    ) -> Awaitable[JsonableCovariantT]:
        """Call the underlying async function directly."""
        return self.fn(*args, **kwargs)

    async def execute(self, tool_call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Execute the async tool using an LLM-provided `ToolCall`."""
        kwargs_callable = cast(AsyncKwargsCallable[JsonableCovariantT], self.fn)
        error: ToolError | None = None
        try:
            kwargs_from_json = json.loads(tool_call.args)
            result = await kwargs_callable(**kwargs_from_json)
        except Exception as e:
            result = str(e)
            error = ToolExecutionError(e)
        return ToolOutput(id=tool_call.id, result=result, error=error, name=self.name)


class ContextTool(
    ToolSchema[ContextToolFn[DepsT, AnyP, JsonableCovariantT]],
    Generic[DepsT, JsonableCovariantT, AnyP],
):
    """Protocol defining a tool that can be used by LLMs.

    A `ContextTool` represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    @classmethod
    def from_function(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls,
        fn: ContextToolFn[DepsT, AnyP, JsonableCovariantT],
        *,
        strict: bool | None = None,
    ) -> ContextTool[DepsT, JsonableCovariantT, AnyP]:
        """Create a `ContextTool` by inspecting a function and its docstring.

        Args:
            fn: The function to extract schema from
            strict: Whether the tool should use strict mode when supported.
                If None, uses provider's default (usually as strict as possible).

        Returns:
            a `ContextTool` representing the function
        """
        schema = ToolSchema.from_function(fn, strict=strict, is_context_tool=True)
        return cls(
            fn=cast(ContextToolFn[DepsT, AnyP, JsonableCovariantT], schema.fn),
            name=schema.name,
            description=schema.description,
            parameters=schema.parameters,
            strict=schema.strict,
        )

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
        kwargs_callable = cast(
            ContextKwargsCallable[DepsT, JsonableCovariantT], self.fn
        )
        error: ToolError | None = None
        try:
            kwargs_from_json = json.loads(tool_call.args)
            result = kwargs_callable(ctx, **kwargs_from_json)
        except Exception as e:
            result = str(e)
            error = ToolExecutionError(e)
        return ToolOutput(id=tool_call.id, result=result, error=error, name=self.name)


class AsyncContextTool(
    ToolSchema[AsyncContextToolFn[DepsT, AnyP, JsonableCovariantT]],
    Generic[DepsT, JsonableCovariantT, AnyP],
):
    """Protocol defining an async tool that can be used by LLMs with context.

    An `AsyncContextTool` represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    @classmethod
    def from_function(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls,
        fn: AsyncContextToolFn[DepsT, AnyP, JsonableCovariantT],
        *,
        strict: bool | None = None,
    ) -> AsyncContextTool[DepsT, JsonableCovariantT, AnyP]:
        """Create an `AsyncContextTool` by inspecting a function and its docstring.

        Args:
            fn: The function to extract schema from
            strict: Whether the tool should use strict mode when supported.
                If None, uses provider's default (usually as strict as possible).

        Returns:
            an `AsyncContextTool` representing the function
        """
        schema = ToolSchema.from_function(fn, strict=strict, is_context_tool=True)
        return cls(
            fn=cast(AsyncContextToolFn[DepsT, AnyP, JsonableCovariantT], schema.fn),
            name=schema.name,
            description=schema.description,
            parameters=schema.parameters,
            strict=schema.strict,
        )

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
        kwargs_callable = cast(
            AsyncJsonKwargsCallable[DepsT, JsonableCovariantT], self.fn
        )
        error: ToolError | None = None
        try:
            kwargs_from_json = json.loads(tool_call.args)
            result = await kwargs_callable(ctx, **kwargs_from_json)
        except Exception as e:
            result = str(e)
            error = ToolExecutionError(e)
        return ToolOutput(id=tool_call.id, result=result, error=error, name=self.name)
