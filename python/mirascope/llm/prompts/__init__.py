"""The prompt templates module for LLM interactions.

This module defines the prompt templates used in LLM interactions, which are written as
python functions.
"""

from . import _utils
from .decorator import prompt
from .protocols import (
    AsyncContextPrompt,
    AsyncContextPromptable,
    AsyncPrompt,
    AsyncPromptable,
    ContextPrompt,
    ContextPromptable,
    Prompt,
    Promptable,
    PromptT,
)

__all__ = [
    "AsyncContextPrompt",
    "AsyncContextPromptable",
    "AsyncPrompt",
    "AsyncPromptable",
    "ContextPrompt",
    "ContextPromptable",
    "Prompt",
    "PromptT",
    "Promptable",
    "_utils",
    "prompt",
]
