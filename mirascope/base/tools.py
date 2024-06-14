"""A base interface for using tools (function calling) when calling LLMs."""

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Type, TypeVar, Union

from pydantic import BaseModel, ConfigDict
from pydantic.json_schema import SkipJsonSchema

DEFAULT_TOOL_DOCSTRING = " ".join(
    """
Correctly formatted and typed parameters extracted from the completion. Must include
required parameters and may exclude optional parameters unless present in the text.
    """.strip().split("\n")
)

BaseType = Union[
    str,
    int,
    float,
    bool,
    list,
    set,
    tuple,
]

ToolCallT = TypeVar("ToolCallT", bound=Any)


class BaseTool(BaseModel, Generic[ToolCallT], ABC):
    """A base class for easy use of tools with prompts.

    `BaseTool` is an abstract class interface and should not be used directly. When
    implementing a class that extends `BaseTool`, you must include the original
    `tool_call` from which this till was instantiated. Make sure to skip `tool_call`
    when generating the schema by annotating it with `SkipJsonSchema`.
    """

    tool_call: SkipJsonSchema[ToolCallT]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def name(cls) -> str:
        """Returns the name of the tool."""
        return cls.__name__

    @classmethod
    def description(cls) -> str:
        """Returns the description of the tool."""
        return inspect.cleandoc(cls.__doc__) if cls.__doc__ else DEFAULT_TOOL_DOCSTRING

    @property
    def args(self) -> dict[str, Any]:
        """The arguments of the tool as a dictionary."""
        return {
            field: getattr(self, field)
            for field in self.model_fields
            if field != "tool_call"
        }

    @property
    def fn(self) -> Callable[..., str]:
        """Returns the function that the tool describes."""
        raise RuntimeError("Tool does not have an attached function.")

    def call(self) -> str:
        """Calls the tool's `fn` with the tool's `args`."""
        return self.fn(**self.args)

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

    @classmethod
    @abstractmethod
    def from_tool_call(cls, tool_call: ToolCallT) -> BaseTool:
        """Extracts an instance of the tool constructed from a tool call response."""
        ...  # pragma: no cover

    @classmethod
    @abstractmethod
    def from_model(cls, model: Type[BaseModel]) -> Type[BaseTool]:
        """Constructs a `BaseTool` type from a `BaseModel` type."""
        ...  # pragma: no cover

    @classmethod
    @abstractmethod
    def from_fn(cls, fn: Callable) -> Type[BaseTool]:
        """Constructs a `BaseTool` type from a function."""
        ...  # pragma: no cover

    @classmethod
    @abstractmethod
    def from_base_type(cls, base_type: Type[BaseType]) -> Type[BaseTool]:
        """Constructs a `BaseTool` type from a `BaseType` type."""
        ...  # pragma: no cover
