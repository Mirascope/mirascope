"""Common TypeVar definitions for the LLM module."""

from typing import TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
"""Parameter specification for function signatures.

This ParamSpec is used to preserve function parameter types and signatures
when wrapping functions with decorators or creating generic callable types.
It captures both positional and keyword arguments (*args, **kwargs) while
maintaining their original types.
"""

CovariantT = TypeVar("CovariantT", covariant=True)
"""Type variable for covariant types."""
