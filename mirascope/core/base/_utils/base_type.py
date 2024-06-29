"""This module contains utility functions for base types."""

import inspect
from enum import Enum
from typing import Annotated, Any, Literal, Union, get_origin

BaseType = str | int | float | bool | list | set | tuple


def is_base_type(type_: Any) -> bool:
    """Check if a type is a base type."""
    base_types = {str, int, float, bool, list, set, tuple}
    return (
        (inspect.isclass(type_) and issubclass(type_, Enum))
        or type_ in base_types
        or get_origin(type_) in base_types.union({Literal, Union, Annotated})
    )
