"""Utility for converting a model into a base tool."""

import inspect
from abc import update_abstractmethods
from typing import Any, TypeVar, cast

from pydantic import BaseModel, create_model

from ..from_call_args import is_from_call_args
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
        model: The `BaseModel` schema to convert.
        base: The base type to extend with the `BaseModel` fields.

    Returns:
        The constructed `BaseModelT` type.
    """
    field_definitions = {
        field_name: (field_info.annotation, field_info)
        for field_name, field_info in model.model_fields.items()
        if not is_from_call_args(field_info)
    }
    tool_type = create_model(
        f"{model.__name__}",
        __base__=base,
        __doc__=model.__doc__ if model.__doc__ else DEFAULT_TOOL_DOCSTRING,
        **cast(dict[str, Any], field_definitions),
    )
    tool_type.model_config = model.model_config | tool_type.model_config
    bases = list(tool_type.__bases__)
    tool_type.__bases__ = tuple(bases) if model in bases else tuple([model] + bases)
    for name, value in inspect.getmembers(model):
        if not hasattr(tool_type, name) or name in ["_name", "_description", "call"]:
            setattr(tool_type, name, value)
    return update_abstractmethods(tool_type)
