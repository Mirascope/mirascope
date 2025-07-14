"""Response formatting interfaces for structuring LLM outputs.

This module provides a way to define structured output formats for LLM responses.
The `@response_format` decorator can be applied to classes to specify how LLM
outputs should be structured and parsed.
"""

from .decorator import (
    ContentResponseFormatDef,
    JsonResponseFormatDef,
    ToolResponseFormatDef,
    response_format,
)
from .from_call_args import FromCallArgs
from .response_format import FormatT, Formattable, ResponseFormat

__all__ = [
    "ContentResponseFormatDef",
    "FormatT",
    "Formattable",
    "FromCallArgs",
    "JsonResponseFormatDef",
    "ResponseFormat",
    "ToolResponseFormatDef",
    "response_format",
]
