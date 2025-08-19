"""Typing for JSON serializable objects."""

from collections.abc import Mapping, Sequence
from typing import Protocol, TypeAlias
from typing_extensions import TypeVar


class JsonableObject(Protocol):
    """Protocol for JSON-serializable objects.

    This protocol defines the interface for objects that can be serialized to
    JSON. It is used to annotate the `JsonableType` type alias.
    """

    def json(self) -> str:
        """Serialize the object as a JSON string."""
        ...


Jsonable: TypeAlias = (
    None
    | str
    | int
    | float
    | bool
    | Sequence["Jsonable"]
    | Mapping[str, "Jsonable"]
    | JsonableObject
)
"""Simple type alias for JSON-serializable types."""


JsonableT = TypeVar("JsonableT", bound=Jsonable)
"""Type variable for tool output types.

This TypeVar represents the return type of tool functions, which must be
serializable to JSON (bound to Jsonable) for LLM consumption.
"""


JsonableCovariantT = TypeVar(
    "JsonableCovariantT", covariant=True, bound=Jsonable, default=Jsonable
)
"""Type variable for covariant types that are Jsonable."""
