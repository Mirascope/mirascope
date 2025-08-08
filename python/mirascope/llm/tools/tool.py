"""The `Tool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from ..content import ToolCall, ToolOutput
from ..types import Jsonable, JsonableCovariantT, P
from .base_tool import BaseTool

ToolT = TypeVar(
    "ToolT",
    bound="Tool[..., Jsonable] | AsyncTool[..., Jsonable]",
    covariant=True,
)


@dataclass
class Tool(BaseTool[P, JsonableCovariantT]):
    """A tool that can be used by LLMs.

    A Tool represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    fn: Callable[P, JsonableCovariantT]
    """The function that implements the tool's functionality."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> JsonableCovariantT:
        """Call the underlying function directly."""
        return self.fn(*args, **kwargs)

    def execute(self, tool_call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Execute the tool using an LLM-provided ToolCall."""
        result = self.fn(**tool_call.args)  # type: ignore[reportCallIssue]
        return ToolOutput(id=tool_call.id, value=result)


@dataclass
class AsyncTool(BaseTool[P, JsonableCovariantT]):
    """An async tool that can be used by LLMs.

    An AsyncTool represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    fn: Callable[P, Awaitable[JsonableCovariantT]]
    """The async function that implements the tool's functionality."""

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Awaitable[JsonableCovariantT]:
        """Call the underlying async function directly."""
        return self.fn(*args, **kwargs)

    async def execute(self, tool_call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Execute the async tool using an LLM-provided ToolCall."""
        result = await self.fn(**tool_call.args)  # type: ignore[reportCallIssue]
        return ToolOutput(id=tool_call.id, value=result)
