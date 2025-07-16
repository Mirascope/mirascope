"""The `ContextTool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Concatenate, Generic

from ..content import ToolCall, ToolOutput
from ..context import Context, DepsT
from ..types import JsonableCovariantT, P
from .base_tool import BaseTool


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
