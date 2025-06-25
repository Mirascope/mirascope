"""The `llm.models` module for implementing the `Model` interface and utilities.

This module provides a unified interface for interacting with different LLM models
through the `Model` abstract class. The `llm.model` context manager allows you to
easily run an LLM call with a model specified at runtime rather than definition
time.
"""

from contextlib import suppress

from .base import LLM, Client, Params
from .context import model
from .register import (
    ANTHROPIC_REGISTERED_LLMS,
    GOOGLE_REGISTERED_LLMS,
    OPENAI_REGISTERED_LLMS,
    REGISTERED_LLMS,
)

with suppress(ImportError):
    from .anthropic import Anthropic, AnthropicClient, AnthropicParams

__all__ = [
    "ANTHROPIC_REGISTERED_LLMS",
    "GOOGLE_REGISTERED_LLMS",
    "LLM",
    "OPENAI_REGISTERED_LLMS",
    "REGISTERED_LLMS",
    "Anthropic",
    "AnthropicClient",
    "AnthropicParams",
    "Client",
    "Params",
    "model",
]
