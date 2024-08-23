"""This module contains the type definition for the base call parameters."""

from typing import Generic, TypeVar

from typing_extensions import NotRequired, TypedDict

from mirascope.core import BaseTool

_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)


class BaseCallParams(Generic[_BaseToolT], TypedDict, total=False):
    tools: NotRequired[list[_BaseToolT]]
