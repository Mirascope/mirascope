"""Response formatting interfaces for structuring LLM outputs.

This module provides a way to define structured output formats for LLM responses.
The `@format` decorator can be applied to classes to specify how LLM
outputs should be structured and parsed.
"""

from .decorator import (
    format,
)
from .from_call_args import FromCallArgs
from .types import Format, FormatT, Formattable, FormattingMode

__all__ = [
    "Format",
    "FormatT",
    "Formattable",
    "FormattingMode",
    "FromCallArgs",
    "format",
]
