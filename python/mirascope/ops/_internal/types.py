"""Type definitions for Mirascope tracing and capabilities."""

from collections.abc import Mapping, Sequence
from typing import ParamSpec, TypeAlias
from typing_extensions import TypeVar

P = ParamSpec("P")
R = TypeVar("R", infer_variance=True)

Jsonable: TypeAlias = (
    None | str | int | float | bool | Sequence["Jsonable"] | Mapping[str, "Jsonable"]
)
"""Simple type alias for JSON-serializable types."""
