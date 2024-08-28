"""This module contains utility functions for base types."""

import inspect
from enum import Enum
from typing import (
    Annotated,
    Any,
    Literal,
    TypeAlias,
    TypeVar,
    Union,
    get_origin,
)

from pydantic import BaseModel
from typing_extensions import TypeIs

BaseType: TypeAlias = str | int | float | bool | bytes | list | set | tuple | dict

_BaseModelT = TypeVar("_BaseModelT", bound=BaseModel)
_BaseTypeT = TypeVar("_BaseTypeT", bound=BaseType)


def is_base_type(type_: Any) -> TypeIs[type[BaseType]]:  # noqa: ANN401
    """Check if a type is a base type."""
    base_types = {str, int, float, bool, bytes, list, set, tuple, dict}
    return (
        (inspect.isclass(type_) and issubclass(type_, Enum))
        or type_ in base_types
        or get_origin(type_) in base_types.union({Literal, Union, Annotated})
    )
