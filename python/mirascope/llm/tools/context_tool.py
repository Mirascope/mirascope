"""The `ContextTool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Concatenate, Generic

from typing_extensions import TypeVar

from ..content import ToolCall, ToolOutput
from ..context import Context, DepsT
from ..types import JsonableCovariantT, PWithDefault
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
    ToolSchema[Callable[Concatenate[Context[DepsT], PWithDefault], JsonableCovariantT]],
    Generic[DepsT, PWithDefault, JsonableCovariantT],
):
    """Protocol defining a tool that can be used by LLMs.

    A `ContextTool` represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __call__(
        self,
        ctx: Context[DepsT],
        *args: PWithDefault.args,
        **kwargs: PWithDefault.kwargs,
    ) -> JsonableCovariantT:
        raise NotImplementedError()

    def execute(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> ToolOutput[JsonableCovariantT]:
        """Call the tool using an LLM-provided `ToolCall`."""
        raise NotImplementedError()


class AsyncContextTool(
    ToolSchema[Callable[Concatenate[Context[DepsT], PWithDefault], JsonableCovariantT]],
    Generic[DepsT, PWithDefault, JsonableCovariantT],
):
    """Protocol defining an async tool that can be used by LLMs with context.

    An `AsyncContextTool` represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __call__(
        self,
        ctx: Context[DepsT],
        *args: PWithDefault.args,
        **kwargs: PWithDefault.kwargs,
    ) -> Awaitable[JsonableCovariantT]:
        raise NotImplementedError()

    async def execute(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> ToolOutput[JsonableCovariantT]:
        """Call the tool using an LLM-provided `ToolCall`."""
        raise NotImplementedError()
