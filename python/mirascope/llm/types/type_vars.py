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

PWithDefault = ParamSpec("PWithDefault", default=...)
"""Parameter specification for function signatures, with a default.

This ParamSpec has a default of ... set, which is useful in cases where we want the
ParamSpec type var not to come first.
"""

CovariantT = TypeVar("CovariantT", covariant=True)
"""Type variable for covariant types."""
