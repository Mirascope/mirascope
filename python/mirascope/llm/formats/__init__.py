"""Response formatting interfaces for structuring LLM outputs.

This module provides a way to define structured output formats for LLM responses.
The `@format` decorator can be applied to classes to specify how LLM
outputs should be structured and parsed.
"""

from .decorator import (
    ContentFormatDef,
    JsonFormatDef,
    ToolFormatDef,
    format,
)
from .format import Format, FormatT, Formattable
from .from_call_args import FromCallArgs

__all__ = [
    "ContentFormatDef",
    "Format",
    "FormatT",
    "Formattable",
    "FromCallArgs",
    "JsonFormatDef",
    "ToolFormatDef",
    "format",
]
