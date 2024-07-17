"""This module defines the base class for tools used in LLM calls."""

import inspect
from abc import abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict

from . import _utils


class BaseTool(BaseModel):
    """A class for defining tools for LLM calls."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def _name(cls) -> str:
        """Returns the name of the tool."""
        return cls.__name__

    @classmethod
    def _description(cls) -> str:
        """Returns the description of the tool."""
        return (
            inspect.cleandoc(cls.__doc__)
            if cls.__doc__
            else _utils.DEFAULT_TOOL_DOCSTRING
        )

    @property
    def args(self) -> dict[str, Any]:
        """The arguments of the tool as a dictionary."""
        return {
            field: getattr(self, field)
            for field in self.model_fields
            if field != "tool_call"
        }

    @abstractmethod
    def call(self) -> Any:
        """The method to call the tool."""
        ...  # pragma: no cover

    @abstractmethod
    async def call_async(self) -> Any:
        """The method to call the tool asynchronously."""
        ...  # pragma: no cover
