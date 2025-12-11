"""The `llm.models` module for implementing the `Model` interface and utilities.

This module provides a unified interface for interacting with different LLM models
through the `Model` class. The `llm.model()` context manager allows you to override
the model at runtime, and `llm.use_model()` retrieves the model from context or
creates a default one.
"""

from .models import Model, model, model_from_context, use_model

__all__ = [
    "Model",
    "model",
    "model_from_context",
    "use_model",
]
