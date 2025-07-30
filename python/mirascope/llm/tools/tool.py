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
    """Protocol defining a tool that can be used by LLMs.

    A Tool represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    fn: Callable[P, JsonableCovariantT]
    """The function that implements the tool's functionality."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> JsonableCovariantT:
        return self.fn(*args, **kwargs)

    def execute(self, call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Call the tool using an LLM-provided ToolCall."""
        raise NotImplementedError()


@dataclass
class AsyncTool(BaseTool[P, JsonableCovariantT]):
    """Protocol defining an async tool that can be used by LLMs.

    An AsyncTool represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    fn: Callable[P, Awaitable[JsonableCovariantT]]
    """The async function that implements the tool's functionality."""

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Awaitable[JsonableCovariantT]:
        return self.fn(*args, **kwargs)

    async def execute(self, call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Call the tool using an LLM-provided ToolCall."""
        raise NotImplementedError()
