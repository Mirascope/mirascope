"""Response formatting interfaces for structuring LLM outputs.

This module provides a way to define structured output formats for LLM responses.
The `@format` decorator can be applied to classes to specify how LLM
outputs should be structured and parsed.

The `@output_parser` decorator can be used to create custom parsers for non-JSON
formats like XML, YAML, CSV, or any custom text structure.
"""

from .format import Format, format, resolve_format
from .from_call_args import FromCallArgs
from .output_parser import OutputParser, is_output_parser, output_parser
from .partial import Partial
from .primitives import (
    PrimitiveType,
    PrimitiveWrapperModel,
    create_wrapper_model,
    is_primitive_type,
)
from .types import FormatSpec, FormattableT, FormattingMode

__all__ = [
    "Format",
    "FormatSpec",
    "FormattableT",
    "FormattingMode",
    "FromCallArgs",
    "OutputParser",
    "Partial",
    "PrimitiveType",
    "PrimitiveWrapperModel",
    "create_wrapper_model",
    "format",
    "is_output_parser",
    "is_primitive_type",
    "output_parser",
    "resolve_format",
]
