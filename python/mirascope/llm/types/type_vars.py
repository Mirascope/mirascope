"""Common TypeVar definitions for the LLM module."""

from typing_extensions import ParamSpec, TypeVar

from .jsonable import Jsonable

ToolReturnT = TypeVar("ToolReturnT", bound=Jsonable)
"""Type variable for tool output types.

This TypeVar represents the return type of tool functions, which must be
serializable to JSON (bound to Jsonable) for LLM consumption.
"""

FormatT = TypeVar("FormatT", bound=object | None, default=None)
"""Type variable for structured response format types.

This TypeVar represents the type of structured output format that LLM responses
can be parsed into, such as Pydantic models, dataclasses, or custom classes.
It can be None for unstructured responses and defaults to None when no specific
format is required.
"""

RequiredFormatT = TypeVar("RequiredFormatT", bound=object)
"""Type variable for non-optional response format types.

This TypeVar represents the type of structured output format that LLM responses
can be parsed into, such as Pydantic models, dataclasses, or custom classes.
Unlike FormatT, RequiredFormatT is used in cases where a format is mandatory (not None).
"""

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
