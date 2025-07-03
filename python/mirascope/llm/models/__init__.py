"""The `llm.models` module for implementing the `LLM` interface and utilities.

This module provides a unified interface for interacting with different LLM models
through the `LLM` class. The `llm.model` context manager allows you to
easily run an LLM call with a model specified at runtime rather than definition
time.
"""

from .base import LLM
from .context import model
from .models import Anthropic, Google, OpenAI

__all__ = [
    "LLM",
    "Anthropic",
    "Google",
    "OpenAI",
    "model",
]
