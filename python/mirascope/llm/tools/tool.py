"""The `Tool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

from ..content import ToolCall, ToolOutput
from ..types import JsonableCovariantT, P
from .tool_schema import ToolSchema

ToolT = TypeVar(
    "ToolT",
    bound="Tool | AsyncTool",
    covariant=True,
)


class Tool(ToolSchema[Callable[P, JsonableCovariantT]], Generic[P, JsonableCovariantT]):
    """A tool that can be used by LLMs.

    A `Tool` represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> JsonableCovariantT:
        """Call the underlying function directly."""
        return self.fn(*args, **kwargs)

    def execute(self, tool_call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Execute the tool using an LLM-provided `ToolCall`."""
        args = json.loads(tool_call.args)
        result = self.fn(**args)  # type: ignore[reportCallIssue]
        return ToolOutput(id=tool_call.id, value=result, name=self.name)


class AsyncTool(
    ToolSchema[Callable[P, Awaitable[JsonableCovariantT]]],
    Generic[P, JsonableCovariantT],
):
    """An async tool that can be used by LLMs.

    An `AsyncTool` represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Awaitable[JsonableCovariantT]:
        """Call the underlying async function directly."""
        return self.fn(*args, **kwargs)

    async def execute(self, tool_call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Execute the async tool using an LLM-provided `ToolCall`."""
        args = json.loads(tool_call.args)
        result = await self.fn(**args)  # type: ignore[reportCallIssue]
        return ToolOutput(id=tool_call.id, value=result, name=self.name)
