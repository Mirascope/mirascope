"""The prompt templates module for LLM interactions.

This module defines the prompt templates used in LLM interactions, which are written as
python functions.
"""

from .decorator import (
    AsyncContextPromptable,
    AsyncContextPromptTemplate,
    AsyncPromptable,
    AsyncPromptTemplate,
    ContextPromptable,
    ContextPromptTemplate,
    Promptable,
    PromptTemplate,
    prompt_template,
)

__all__ = [
    "AsyncContextPromptTemplate",
    "AsyncContextPromptable",
    "AsyncPromptTemplate",
    "AsyncPromptable",
    "ContextPromptTemplate",
    "ContextPromptable",
    "PromptTemplate",
    "Promptable",
    "prompt_template",
]
