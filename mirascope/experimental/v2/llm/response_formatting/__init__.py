"""Response formatting interfaces for structuring LLM outputs.

This module provides a way to define structured output formats for LLM responses.
The `@response_format` decorator can be applied to classes to specify how LLM
outputs should be structured and parsed.
"""

from .decorator import response_format
from .from_call_args import FromCallArgs
from .response_format import ResponseFormat

__all__ = ["FromCallArgs", "ResponseFormat", "response_format"]
