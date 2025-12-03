"""Mirascope Ops exception hierarchy for unified error handling across providers."""


class MirascopeOpsError(Exception):
    """Base exception for all Mirascope Ops errors."""

    original_exception: Exception | None


class ConfigurationError(MirascopeOpsError):
    """Raised when Ops configuration is invalid."""


class ClosureComputationError(MirascopeOpsError):
    """Raised when the closure for a function cannot be computed properly."""

    qualified_name: str

    def __init__(self, qualified_name: str) -> None:
        """Initializes an instance of `ClosureComputationError`."""
        self.qualified_name = qualified_name
