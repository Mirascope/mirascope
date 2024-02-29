"""A base tool class for easy use of tools with prompts."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from pydantic import BaseModel


class BaseTool(BaseModel, ABC):
    """A base class for easy use of tools with prompts.

    `BaseTool` is an abstract class interface and should not be used directly.
    """

    @property
    def fn(self) -> Optional[Callable]:
        """Returns the function that the tool describes."""
        return None

    @classmethod
    @abstractmethod
    def tool_schema(cls) -> Any:
        """Constructs a tool schema from the `BaseModel` schema defined."""
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_tool_call(cls, tool_call: Any) -> BaseTool:
        """Extracts an instance of the tool constructed from a tool call response."""
        raise NotImplementedError()
