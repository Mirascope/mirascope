"""Common TypeVar definitions for the LLM module."""

from typing_extensions import ParamSpec, TypeVar

from .jsonable import Jsonable

P = ParamSpec("P")
"""Parameter specification for function signatures.

This ParamSpec is used to preserve function parameter types and signatures
when wrapping functions with decorators or creating generic callable types.
It captures both positional and keyword arguments (*args, **kwargs) while
maintaining their original types.
"""

JsonableT = TypeVar("JsonableT", bound=Jsonable)
"""Type variable for tool output types.

This TypeVar represents the return type of tool functions, which must be
serializable to JSON (bound to Jsonable) for LLM consumption.
"""

CovariantT = TypeVar("CovariantT", covariant=True)
"""Type variable for covariant types."""

JsonableCovariantT = TypeVar("JsonableCovariantT", covariant=True, bound=Jsonable)
"""Type variable for covariant types that are Jsonable."""
