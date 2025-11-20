"""Mirascope exception hierarchy for unified error handling across providers."""


class MirascopeError(Exception):
    """Base exception for all Mirascope errors."""

    original_exception: Exception | None
