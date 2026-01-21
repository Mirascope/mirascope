"""Utilities for handling primitive types in formatting."""

import inspect
from enum import Enum
from types import UnionType
from typing import (
    Annotated,
    Any,
    Literal,
    Protocol,
    TypeAlias,
    Union,
    cast,
    get_args,
    get_origin,
)
from typing_extensions import TypeIs

from pydantic import create_model

PrimitiveType: TypeAlias = (
    str
    | int
    | float
    | bool
    | bytes
    | list[Any]
    | set[Any]
    | tuple[Any, ...]
    | dict[Any, Any]
)
"""Primitive types that can be used with format parameter.

These types are automatically wrapped in a BaseModel for schema generation,
then unwrapped after validation to return the primitive value.
"""


class PrimitiveWrapperModel(Protocol):
    """Protocol for wrapper models with an output field."""

    output: Any
    model_fields: Any

    def __init__(self, *, output: Any) -> None: ...  # noqa: ANN401

    @classmethod
    def model_json_schema(cls) -> dict[str, Any]: ...

    @classmethod
    def model_validate_json(cls, json_data: str) -> "PrimitiveWrapperModel": ...


def is_primitive_type(
    type_: Any,  # noqa: ANN401
) -> TypeIs[type[PrimitiveType]]:
    """Check if a type is a primitive type that needs wrapping.

    Returns True for:
    - Basic primitives: str, int, float, bool, bytes, list, set, tuple, dict
    - Enum types
    - Generic types with primitive origins: list[Book], dict[str, int]
    - Literal types
    - Union types (including Optional)
    - Annotated types

    Returns False for:
    - BaseModel subclasses (already have model_json_schema)
    - None/NoneType

    Args:
        type_: The type to check

    Returns:
        True if the type is a primitive that needs wrapping

    Example:
        >>> is_primitive_type(str)
        True
        >>> is_primitive_type(list[int])
        True
        >>> from pydantic import BaseModel
        >>> class Book(BaseModel):
        ...     title: str
        >>> is_primitive_type(Book)
        False
    """
    primitive_types: set[type[PrimitiveType]] = {
        str,
        int,
        float,
        bool,
        bytes,
        list,
        set,
        tuple,
        dict,
    }
    special_types: set[Any] = {Annotated, Literal, Union, UnionType}

    return (
        (inspect.isclass(type_) and issubclass(type_, Enum))
        or type_ in primitive_types
        or get_origin(type_) in primitive_types.union(special_types)
    )


def _get_type_name(type_: Any) -> str:  # noqa: ANN401
    """Extract a clean name from a type for use in model naming.

    Handles Annotated types by extracting the underlying type,
    and generates clean names for generic types.

    Args:
        type_: The type to extract a name from

    Returns:
        A clean string suitable for use in a Python class name

    Example:
        >>> _get_type_name(str)
        'str'
        >>> _get_type_name(list[int])
        'list_int_'
    """
    # Import Annotated locally
    # Check if this is an Annotated type
    if get_origin(type_) in {Annotated}:
        # For Annotated types, use the first arg (the actual type)
        return _get_type_name(get_args(type_)[0])

    # If the type has a __name__ attribute, use it
    if hasattr(type_, "__name__"):
        return type_.__name__

    # For complex generics like list[Book], use string representation
    type_str = str(type_)

    # Clean up the string to make it a valid Python identifier
    # Replace brackets and commas with underscores
    clean = (
        type_str.replace("[", "_")
        .replace("]", "_")
        .replace(", ", "_")
        .replace(" ", "")
        .replace("'", "")
        .replace('"', "")
    )

    return clean


def create_wrapper_model(
    primitive_type: Any,  # noqa: ANN401
) -> type[PrimitiveWrapperModel]:
    """Create a wrapper BaseModel for a primitive type.

    The wrapper has a single field called "output" containing the primitive value.
    Uses Pydantic's create_model() to generate the wrapper dynamically.

    Args:
        primitive_type: The primitive type to wrap

    Returns:
        A dynamically created BaseModel with an "output" field

    Example:
        >>> wrapper = create_wrapper_model(str)
        >>> instance = wrapper(output="hello")
        >>> instance.output
        'hello'

        >>> from pydantic import BaseModel
        >>> class Book(BaseModel):
        ...     title: str
        >>> wrapper = create_wrapper_model(list[Book])
        >>> books = [Book(title="Test")]
        >>> instance = wrapper(output=books)
        >>> len(instance.output)
        1
    """
    # Get a clean name for the wrapper class
    type_name = _get_type_name(primitive_type)

    # Create wrapper model with "output" field (required)
    wrapper = create_model(
        f"{type_name}Output",
        __doc__=f"Wrapper for primitive type {type_name}",
        output=(primitive_type, ...),  # ... means required
    )

    return cast(type[PrimitiveWrapperModel], wrapper)
