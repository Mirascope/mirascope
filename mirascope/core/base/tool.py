"""This module defines the base class for tools used in LLM calls.

usage-docs: learn/tools.md#the-basetool-class
"""

from __future__ import annotations

import inspect
from abc import abstractmethod
from typing import Any, Callable, ClassVar, TypeVar, cast

from pydantic import BaseModel, ConfigDict

from . import _utils

_BaseToolT = TypeVar("_BaseToolT")


class BaseTool(BaseModel):
    '''A class for defining tools for LLM calls.

    Example:

    ```python
    from mirascope.core import BaseTool
    from pydantic import Field


    class FormatBook(BaseTool):
        """Returns a nicely formatted book recommendation."""

        title: str = Field(..., description="The title of the book.")
        author: str = Field(..., description="The author of the book.")

        def call(self) -> str:
            return f"{self.title} by {self.author}"
    ```
    '''

    __custom_name__: ClassVar[str] = ""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def _name(cls) -> str:
        """Returns the name of the tool."""
        return cls.__custom_name__ if cls.__custom_name__ else cls.__name__

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

    @classmethod
    def model_tool_schema(cls) -> dict[str, Any]:
        """Returns the model_json_schema modified for reduced token usage."""
        model_schema = cls.model_json_schema()
        model_schema.pop("title", None)
        model_schema.pop("description", None)

        def remove_schema_titles(obj):
            if isinstance(obj, dict):
                # Remove the 'title' key only if it's a direct child of a schema object
                if "type" in obj or "$ref" in obj or "properties" in obj:
                    obj.pop("title", None)

                # Recursively process nested objects
                for key, value in list(obj.items()):
                    obj[key] = remove_schema_titles(value)
            elif isinstance(obj, list):
                # Recursively process list items
                return [remove_schema_titles(item) for item in obj]

            return obj

        return cast(dict[str, Any], remove_schema_titles(model_schema))

    @classmethod
    def type_from_fn(cls: _BaseToolT, fn: Callable) -> _BaseToolT:
        """Returns this tool type converted from a function.

        Args:
            fn: The function to convert into this tool type.
        """
        return _utils.convert_function_to_base_tool(fn, cls)  # type: ignore

    @classmethod
    def type_from_base_model_type(
        cls: _BaseToolT, tool_type: type[BaseModel]
    ) -> _BaseToolT:
        """Returns this tool type converted from a given base tool type.

        Args:
            tool_type: The tool type to convert into this tool type. This can be a
                custom `BaseTool` or `BaseModel` definition.
        """
        return _utils.convert_base_model_to_base_tool(tool_type, cls)  # type: ignore

    @classmethod
    def type_from_base_type(
        cls: _BaseToolT, base_type: type[_utils.BaseType]
    ) -> _BaseToolT:
        """Returns this tool type converted from a base type.

        Args:
            base_type: The base type (e.g. `int`) to convert into this tool type.
        """
        return _utils.convert_base_type_to_base_tool(base_type, cls)  # type: ignore
