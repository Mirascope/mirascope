"""The prompt templates module for LLM interactions.

This module defines the prompt templates used in LLM interactions, which are written as
python functions.
"""

from .decorator import (
    AsyncContextPrompt,
    AsyncContextPromptable,
    AsyncPrompt,
    AsyncPromptable,
    ContextPrompt,
    ContextPromptable,
    Prompt,
    Promptable,
    PromptDecorator,
    prompt,
)

__all__ = [
    "AsyncContextPromptable",
    "AsyncContextPrompt",
    "AsyncPromptable",
    "AsyncPrompt",
    "ContextPromptable",
    "ContextPrompt",
    "Promptable",
    "Prompt",
    "PromptDecorator",
    "prompt",
]
