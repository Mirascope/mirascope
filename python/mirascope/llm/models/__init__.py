"""The `llm.models` module for implementing the `Model` interface and utilities.

This module provides a unified interface for interacting with different LLM models
through the `Model` abstract class. The `llm.model` context manager allows you to
easily run an LLM call with a model specified at runtime rather than definition
time.
"""

from .models import Model, get_model_from_context, model

__all__ = [
    "Model",
    "get_model_from_context",
    "model",
]
