"""The `BaseTool` class for defining tools."""

import inspect
from abc import abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict

from .._internal import utils


class BaseTool(BaseModel):
    """A class for defining tools for LLM calls."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def name(cls) -> str:
        """Returns the name of the tool."""
        return cls.__name__

    @classmethod
    def description(cls) -> str:
        """Returns the description of the tool."""
        return (
            inspect.cleandoc(cls.__doc__)
            if cls.__doc__
            else utils.DEFAULT_TOOL_DOCSTRING
        )

    @classmethod
    def tool_schema(cls) -> Any:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined."""
        model_schema = cls.model_json_schema()
        model_schema.pop("title", None)
        model_schema.pop("description", None)

        fn = {"name": cls.name(), "description": cls.description()}
        if model_schema["properties"]:
            fn["parameters"] = model_schema  # type: ignore

        return fn

    @abstractmethod
    def call(self) -> Any:
        """The method to call the tool."""
        ...  # pragma: no cover
