"""This module contains the function to extract the return value of a tool."""

from typing import TypeVar

import jiter
from pydantic import BaseModel

from .._partial import partial
from ._base_type import BaseType, is_base_type
from ._convert_base_type_to_base_tool import convert_base_type_to_base_tool

_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)


def extract_tool_return(
    response_model: type[_ResponseModelT],
    json_output: str | object,
    allow_partial: bool,
) -> _ResponseModelT:
    json_obj = (
        jiter.from_json(
            json_output.encode(),
            partial_mode="trailing-strings" if allow_partial else "off",
        )
        if isinstance(json_output, str)
        else json_output
    )
    if is_base_type(response_model):
        temp_model = convert_base_type_to_base_tool(response_model, BaseModel)  # type: ignore
        if allow_partial:
            return partial(temp_model).model_validate(json_obj).value  # type: ignore
        return temp_model.model_validate(json_obj).value  # type: ignore

    if allow_partial:
        return partial(response_model).model_validate(json_obj)  # type: ignore
    return response_model.model_validate(json_obj)  # type: ignore
