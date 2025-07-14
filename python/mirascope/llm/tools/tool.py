"""The `Tool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..content import ToolCall, ToolOutput
from ..types import JsonableCovariantT, P
from .async_tool import AsyncTool
from .base_tool import BaseTool


@dataclass
class Tool(BaseTool[P, JsonableCovariantT]):
    """Protocol defining a tool that can be used by LLMs.

    A Tool represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    fn: Callable[P, JsonableCovariantT]
    """The function that implements the tool's functionality."""

    def call(self, call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Call the tool using an LLM-provided ToolCall."""
        raise NotImplementedError()

    def to_async(self) -> AsyncTool:
        """Convert this tool into an async tool for usage alongside other async tools."""
        raise NotImplementedError()
