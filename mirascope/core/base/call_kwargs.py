"""This module contains the type definition for the base call keyword arguments."""

from typing import Generic, TypeVar

from typing_extensions import NotRequired

from .call_params import BaseCallParams

_ToolSchemaT = TypeVar("_ToolSchemaT")


class BaseCallKwargs(BaseCallParams, Generic[_ToolSchemaT]):
    tools: NotRequired[list[_ToolSchemaT]]
