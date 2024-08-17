"""This module contains the `setup_extract_tool` function."""

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
        return convert_base_type_to_base_tool(response_model, tool_type)  # type: ignore
    return convert_base_model_to_base_tool(response_model, tool_type)  # type: ignore
