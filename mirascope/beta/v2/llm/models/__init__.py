"""The `llm.models` module for implementing the `Model` interface and utilities.

This module provides a unified interface for interacting with different LLM models
through the `Model` abstract class. The `llm.model` context manager allows you to
easily run an LLM generation with a model specified at runtime rather than definition
time.
"""

from .base import LLM, Client, Params
from .context import model

__all__ = ["LLM", "Client", "Params", "model"]
