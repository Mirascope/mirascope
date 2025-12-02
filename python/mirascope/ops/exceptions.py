"""Mirascope Ops exception hierarchy for unified error handling across providers."""


class MirascopeOpsError(Exception):
    """Base exception for all Mirascope Ops errors."""

    original_exception: Exception | None


class ConfigurationError(MirascopeOpsError):
    """Raised when Ops configuration is invalid."""
