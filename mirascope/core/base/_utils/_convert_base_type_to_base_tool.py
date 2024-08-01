"""This module contains the `convert_base_type_to_base_tool` function."""

from typing import Annotated, TypeVar, get_args, get_origin

from pydantic import BaseModel, create_model

from ._base_type import BaseType
from ._default_tool_docstring import DEFAULT_TOOL_DOCSTRING

BaseToolT = TypeVar("BaseToolT", bound=BaseModel)


def convert_base_type_to_base_tool(
    schema: type[BaseType], base: type[BaseToolT]
) -> type[BaseToolT]:
    """Converts a `BaseType` to a `BaseToolT` type."""
    if get_origin(schema) == Annotated:
        schema.__name__ = get_args(schema)[0].__name__
    return create_model(
        schema.__name__,
        __base__=base,
        __doc__=DEFAULT_TOOL_DOCSTRING,
        value=(schema, ...),
    )
