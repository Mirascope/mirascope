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
    PromptableDecorator,
    PromptTemplate,
    PromptTemplateDecorator,
    prompt_template,
)

__all__ = [
    "AsyncContextPromptable",
    "AsyncContextPromptTemplate",
    "AsyncPromptable",
    "AsyncPromptTemplate",
    "ContextPromptable",
    "ContextPromptTemplate",
    "Promptable",
    "PromptTemplate",
    "PromptableDecorator",
    "PromptTemplateDecorator",
    "prompt_template",
]
