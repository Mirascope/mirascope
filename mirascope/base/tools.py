"""A base interface for using tools (function calling) when calling LLMs."""

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from inspect import Parameter, isclass, signature
from typing import (
    Annotated,
    Any,
    Callable,
    Generic,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from docstring_parser import parse
from pydantic import BaseModel, ConfigDict, create_model
from pydantic.fields import FieldInfo
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
    def from_model(cls, model: type[BaseModel]) -> type[BaseTool]:
        """Constructs a `BaseTool` type from a `BaseModel` type."""
        ...  # pragma: no cover

    @classmethod
    @abstractmethod
    def from_fn(cls, fn: Callable) -> type[BaseTool]:
        """Constructs a `BaseTool` type from a function."""
        ...  # pragma: no cover

    @classmethod
    @abstractmethod
    def from_base_type(cls, base_type: type[BaseType]) -> type[BaseTool]:
        """Constructs a `BaseTool` type from a `BaseType` type."""
        ...  # pragma: no cover


BaseToolT = TypeVar("BaseToolT", bound=BaseTool)


def tool_fn(fn: Callable) -> Callable[[type[BaseToolT]], type[BaseToolT]]:
    """A decorator for adding a function to a tool class.

    Adding this decorator will add an `fn` property to the tool class that returns the
    function that the tool describes. This is convenient for calling the function given
    an instance of the tool.

    Args:
        fn: The function to add to the tool class.

    Returns:
        The decorated tool class.
    """

    def decorator(cls: type[BaseToolT]) -> type[BaseToolT]:
        """A decorator for adding a function to a tool class."""
        setattr(cls, "fn", property(lambda self: fn))
        return cls

    return decorator


def convert_function_to_tool(fn: Callable, base: type[BaseToolT]) -> type[BaseToolT]:
    """Constructs a `BaseToolT` type from the given function.

    This method expects all function parameters to be properly documented in identical
    order with identical variable names, as well as descriptions of each parameter.
    Errors will be raised if any of these conditions are not met.

    Args:
        fn: The function to convert.

    Returns:
        The constructed `BaseToolT` type.

    Raises:
        ValueError: if the given function doesn't have a docstring.
        ValueError: if the given function's parameters don't have type annotations.
        ValueError: if a given function's parameter is in the docstring args section but
            the name doesn't match the docstring's parameter name.
        ValueError: if a given function's parameter is in the docstring args section but
            doesn't have a dosctring description.
    """
    if not fn.__doc__:
        raise ValueError("Function must have a docstring.")

    docstring = parse(fn.__doc__)

    doc = ""
    if docstring.short_description:
        doc = docstring.short_description
    if docstring.long_description:
        doc += "\n\n" + docstring.long_description
    if docstring.returns and docstring.returns.description:
        doc += "\n\n" + "Returns:\n    " + docstring.returns.description

    field_definitions = {}
    hints = get_type_hints(fn)
    for i, parameter in enumerate(signature(fn).parameters.values()):
        if parameter.name == "self" or parameter.name == "cls":
            continue
        if parameter.annotation == Parameter.empty:
            raise ValueError("All parameters must have a type annotation.")

        docstring_description = None
        if i < len(docstring.params):
            docstring_param = docstring.params[i]
            if docstring_param.arg_name != parameter.name:
                raise ValueError(
                    f"Function parameter name {parameter.name} does not match docstring "
                    f"parameter name {docstring_param.arg_name}. Make sure that the "
                    "parameter names match exactly."
                )
            if not docstring_param.description:
                raise ValueError("All parameters must have a description.")
            docstring_description = docstring_param.description

        field_info = FieldInfo(annotation=hints[parameter.name])
        if parameter.default != Parameter.empty:
            field_info.default = parameter.default
        if docstring_description:  # we check falsy here because this comes from docstr
            field_info.description = docstring_description

        param_name = parameter.name
        if param_name.startswith("model_"):  # model_ is a BaseModel reserved namespace
            param_name = "aliased_" + param_name
            field_info.alias = parameter.name
            field_info.validation_alias = parameter.name
            field_info.serialization_alias = parameter.name

        field_definitions[param_name] = (
            hints[parameter.name],
            field_info,
        )

    model = create_model(
        fn.__name__,
        __base__=base,
        __doc__=doc,
        **cast(dict[str, Any], field_definitions),
    )
    return tool_fn(fn)(model)


def convert_base_model_to_tool(
    schema: type[BaseModel], base: type[BaseToolT]
) -> type[BaseToolT]:
    """Converts a `BaseModel` schema to a `BaseToolT` type.

    By adding a docstring (if needed) and passing on fields and field information in
    dictionary format, a Pydantic `BaseModel` can be converted into an `BaseToolT` for
    performing extraction.

    Args:
        schema: The `BaseModel` schema to convert.

    Returns:
        The constructed `BaseToolT` type.
    """
    field_definitions = {
        field_name: (field_info.annotation, field_info)
        for field_name, field_info in schema.model_fields.items()
    }
    return create_model(
        f"{schema.__name__}",
        __base__=base,
        __doc__=schema.__doc__ if schema.__doc__ else DEFAULT_TOOL_DOCSTRING,
        **cast(dict[str, Any], field_definitions),
    )


def convert_base_type_to_tool(
    schema: type[BaseType], base: type[BaseToolT]
) -> type[BaseToolT]:
    """Converts a `BaseType` to a `BaseToolT` type."""
    if get_origin(schema) == Annotated:
        schema.__name__ = get_args(schema)[0].__name__
    return create_model(
        f"{schema.__name__.title()}",
        __base__=base,
        __doc__=DEFAULT_TOOL_DOCSTRING,
        value=(schema, ...),
    )


class Toolkit:
    """A toolkit for organizing tools under a shared namespace."""

    def __init__(self, tools: list[Union[Callable, type[BaseTool]]], namespace: str):
        """Initializes an instance of `Toolkit` with a list of tools."""
        self.namespace = namespace
        namespaced_tools: list[Union[Callable, type[BaseTool]]] = []
        for tool in tools:
            if isclass(tool):
                name = tool.name()
                setattr(tool, "name", lambda: f"{namespace}.{name}")
                namespaced_tools.append(tool)
            else:  # must be function
                tool.__name__ = f"{namespace}.{tool.__name__}"
                namespaced_tools.append(tool)
        self.tools = namespaced_tools
