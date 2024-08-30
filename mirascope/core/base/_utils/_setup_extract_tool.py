"""This module contains the `setup_extract_tool` function."""

from abc import update_abstractmethods
from typing import TypeVar

from pydantic import BaseModel

from ._base_type import BaseType, is_base_type
from ._convert_base_model_to_base_tool import convert_base_model_to_base_tool
from ._convert_base_type_to_base_tool import convert_base_type_to_base_tool

BaseToolT = TypeVar("BaseToolT", bound=BaseModel)


def setup_extract_tool(
    response_model: type[BaseModel] | type[BaseType], tool_type: type[BaseToolT]
) -> type[BaseToolT]:
    if is_base_type(response_model):
        converted_tool_type = convert_base_type_to_base_tool(response_model, tool_type)
    elif issubclass(response_model, BaseModel):
        converted_tool_type = convert_base_model_to_base_tool(response_model, tool_type)
    else:  # pragma: no cover
        # pyright should work with IsType for the case of BaseModel | BaseType
        # But it doesn't, so we need to cover this
        raise ValueError(
            f"`response_model` must be a BaseModel or a BaseType, not `{response_model}`."
        )
    if not hasattr(response_model, "call"):
        converted_tool_type.call = lambda self: ""  # pyright: ignore [reportAttributeAccessIssue]
    return update_abstractmethods(converted_tool_type)
