"""Mirascope Ops exception hierarchy for unified error handling across providers."""

from ..exceptions import MirascopeError


class ConfigurationError(MirascopeError):
    """Raised when Ops configuration is invalid."""
