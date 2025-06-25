"""Typing for JSON serializable objects."""

from collections.abc import Mapping, Sequence
from typing import Protocol, TypeAlias


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
