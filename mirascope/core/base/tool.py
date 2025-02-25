"""This module defines the base class for tools used in LLM calls.

usage-docs: learn/tools.md
"""

from __future__ import annotations

import inspect
import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, ClassVar, TypeVar

import jiter
from pydantic import BaseModel, ConfigDict
from pydantic.json_schema import (
    DEFAULT_REF_TEMPLATE,
    GenerateJsonSchema,
    JsonSchemaMode,
    JsonSchemaValue,
    SkipJsonSchema,
)
from pydantic_core.core_schema import CoreSchema
from typing_extensions import TypedDict

from . import _utils

_BaseToolT = TypeVar("_BaseToolT", bound=BaseModel)
_ToolSchemaT = TypeVar("_ToolSchemaT")


class ToolConfig(TypedDict, total=False):
    """A base class for tool configurations."""


class GenerateJsonSchemaNoTitles(GenerateJsonSchema):
    _openai_strict: ClassVar[bool] = False

    def _remove_title(self, key: str | None, obj: Any) -> Any:  # noqa: ANN401
        if isinstance(obj, dict):
            if self._openai_strict and "type" in obj and obj["type"] == "object":
                obj["additionalProperties"] = False
            if "type" in obj or "$ref" in obj or "properties" in obj:
                title = obj.pop("title", None)
                if key and title and key.lower() != title.lower():
                    obj["title"] = title

            for key, value in list(obj.items()):
                obj[key] = self._remove_title(key, value)
        elif isinstance(obj, list):
            return [self._remove_title(None, item) for item in obj]

        return obj

    def generate(
        self, schema: CoreSchema, mode: JsonSchemaMode = "validation"
    ) -> JsonSchemaValue:
        json_schema = super().generate(schema, mode=mode)
        json_schema.pop("title", None)
        json_schema.pop("description", None)
        json_schema = self._remove_title(None, json_schema)
        return json_schema


class BaseTool(BaseModel, ABC):
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

    __provider__: ClassVar[str] = "NONE"
    __tool_config_type__: ClassVar[type[ToolConfig]] = ToolConfig
    __custom_name__: ClassVar[str] = ""
    tool_config: ClassVar[ToolConfig] = ToolConfig()
    model_config = ConfigDict(arbitrary_types_allowed=True)
    delta: SkipJsonSchema[str | None] = None

    @classmethod
    def _dict_from_json(cls, json: str, allow_partial: bool = False) -> dict[str, Any]:
        """Returns a dictionary from a JSON string."""
        if not json:
            return {}
        return jiter.from_json(
            json.encode(), partial_mode="trailing-strings" if allow_partial else "off"
        )

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
            if field not in {"tool_call", "delta"}
        }

    @abstractmethod
    def call(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        """The method to call the tool."""
        ...

    @classmethod
    def type_from_fn(cls: type[_BaseToolT], fn: Callable) -> type[_BaseToolT]:
        """Returns this tool type converted from a function.

        Args:
            fn: The function to convert into this tool type.
        """
        return _utils.convert_function_to_base_tool(fn, cls)

    @classmethod
    def type_from_base_model_type(
        cls: type[_BaseToolT], tool_type: type[BaseModel]
    ) -> type[_BaseToolT]:
        """Returns this tool type converted from a given base tool type.

        Args:
            tool_type: The tool type to convert into this tool type. This can be a
                custom `BaseTool` or `BaseModel` definition.
        """
        return _utils.convert_base_model_to_base_tool(tool_type, cls)

    @classmethod
    def type_from_base_type(
        cls: type[_BaseToolT], base_type: type[_utils.BaseType]
    ) -> type[_BaseToolT]:
        """Returns this tool type converted from a base type.

        Args:
            base_type: The base type (e.g. `int`) to convert into this tool type.
        """
        return _utils.convert_base_type_to_base_tool(base_type, cls)

    @classmethod
    def tool_schema(cls) -> Any:  # noqa: ANN401
        raise RuntimeError(
            f"{cls.__name__}.tool_schema() is not implemented. "
            "This method should be implemented in provider-specific tool classes."
        )

    @classmethod
    def model_json_schema(
        cls,
        by_alias: bool = True,
        ref_template: str = DEFAULT_REF_TEMPLATE,
        schema_generator: type[GenerateJsonSchema] = GenerateJsonSchemaNoTitles,
        mode: JsonSchemaMode = "validation",
    ) -> dict[str, Any]:
        """Returns the generated JSON schema for the class."""
        cls.warn_for_unsupported_configurations()
        return super().model_json_schema(
            by_alias=by_alias,
            ref_template=ref_template,
            schema_generator=schema_generator,
            mode=mode,
        )

    @classmethod
    def warn_for_unsupported_configurations(cls) -> None:
        """Warns when a specific provider does not support provided config options."""
        unsupported_tool_keys = _utils.get_unsupported_tool_config_keys(
            cls.tool_config, cls.__tool_config_type__
        )
        if unsupported_tool_keys:
            warnings.warn(
                f"{cls.__provider__} does not support the following tool "
                f"configurations, so they will be ignored: {unsupported_tool_keys}",
                UserWarning,
            )

        if "strict" in cls.model_config and cls.__provider__ not in ["openai", "azure"]:
            warnings.warn(
                f"{cls.__provider__} does not support strict structured outputs, but "
                "you have configured `strict=True` in your `ResponseModelConfigDict`. "
                "Ignoring `strict` as this feature is only supported by OpenAI.",
                UserWarning,
            )
