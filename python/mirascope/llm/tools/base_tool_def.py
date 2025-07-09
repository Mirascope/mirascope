"""The `BaseToolDef` class for defining tools that LLMs can request be called."""

from dataclasses import dataclass
from typing import Generic

from ..types import Jsonable, P, ToolReturnT


@dataclass
class BaseToolDef(Generic[P, ToolReturnT]):
    """Base class defining a tool that can be used by LLMs.

    A ToolDef represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    name: str
    """The name of the tool, used by the LLM to identify which tool to call."""

    description: str
    """Description of what the tool does, extracted from the function's docstring."""

    parameters: dict[str, Jsonable]
    """JSON Schema describing the parameters accepted by the tool."""

    strict: bool
    """Whether the tool should use strict mode when supported by the model."""
