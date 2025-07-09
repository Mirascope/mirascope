"""Common TypeVar definitions for the LLM module."""

from typing_extensions import ParamSpec, TypeVar

T = TypeVar("T", bound=object | None, default=None)

P = ParamSpec("P")
"""Parameter specification for function signatures.

This ParamSpec is used to preserve function parameter types and signatures
when wrapping functions with decorators or creating generic callable types.
It captures both positional and keyword arguments (*args, **kwargs) while
maintaining their original types.
"""

DepsT = TypeVar("DepsT", default=None)
"""Type variable for dependency injection in `llm.Context`.

This TypeVar is used throughout the LLM module to represent the type of
dependencies that are present in `llm.Context`. 
It defaults to None when no dependencies are needed.
"""
