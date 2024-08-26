"""This module contains the type definition for the base call keyword arguments."""

from typing import Generic, TypeVar

from typing_extensions import NotRequired

from .call_params import BaseCallParams

_BaseToolT = TypeVar("_BaseToolT")


class BaseCallKwargs(Generic[_BaseToolT], BaseCallParams):
    tools: NotRequired[list[_BaseToolT]]
