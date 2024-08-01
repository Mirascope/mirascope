"""Utility for converting a model model into a base tool."""

import inspect
from abc import update_abstractmethods
from typing import Any, TypeVar, cast

from pydantic import BaseModel, create_model

from ._default_tool_docstring import DEFAULT_TOOL_DOCSTRING

BaseToolT = TypeVar("BaseToolT", bound=BaseModel)


def convert_base_model_to_base_tool(
    model: type[BaseModel], base: type[BaseToolT]
) -> type[BaseToolT]:
    """Converts a `BaseModel` schema to a `BaseToolT` type.

    By adding a docstring (if needed) and passing on fields and field information in
    dictionary format, a Pydantic `BaseModel` can be converted into an `BaseTool` for
    performing extraction.

    Args:
        schema: The `BaseModel` schema to convert.

    Returns:
        The constructed `BaseModelT` type.
    """
    field_definitions = {
        field_name: (field_info.annotation, field_info)
        for field_name, field_info in model.model_fields.items()
    }
    tool_type = create_model(
        f"{model.__name__}",
        __base__=base,
        __doc__=model.__doc__ if model.__doc__ else DEFAULT_TOOL_DOCSTRING,
        **cast(dict[str, Any], field_definitions),
    )
    for name, value in inspect.getmembers(model):
        if not hasattr(tool_type, name) or name in ["_name", "_description", "call"]:
            setattr(tool_type, name, value)
    return update_abstractmethods(tool_type)
