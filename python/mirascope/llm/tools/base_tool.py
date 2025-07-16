"""The `BaseTool` class for defining tools that LLMs can request be called."""

from dataclasses import dataclass
from typing import Generic, TypeGuard

from typing_extensions import Self

from ..types import Jsonable, JsonableCovariantT, P


@dataclass
class BaseTool(Generic[P, JsonableCovariantT]):
    """Base class defining a tool that can be used by LLMs.

    A Tool represents a function that can be called by an LLM during a call.
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

    def defines(self, tool: "BaseTool") -> TypeGuard[Self]:
        """Check if this ToolDef matches a specific Tool instance.

        This method is used to ensure that the ToolDef was created from a specific
        function, allowing for type-safe access to the return value when calling
        the tool.

        Args:
            tool: The Tool instance to compare against.

        Returns:
            True if the ToolDef defines the Tool instance, False otherwise.
        """
        raise NotImplementedError()
