"""The prompt templates module for LLM interactions.

This module defines the prompt templates used in LLM interactions, which are written as
python functions.
"""

from .decorator import (
    AsyncContextPrompt,
    AsyncPrompt,
    ContextPrompt,
    Prompt,
    PromptDecorator,
    prompt,
)

__all__ = [
    "AsyncContextPrompt",
    "AsyncPrompt",
    "ContextPrompt",
    "Prompt",
    "PromptDecorator",
    "prompt",
]
