"""Utilities for handling optional provider dependencies."""

from collections.abc import Callable


def create_import_error_stub(
    package_name: str, client_name: str
) -> Callable[..., None]:  # pragma: no cover
    """Create a stub that raises ImportError when called.

    Args:
        package_name: The package/extra name (e.g., "anthropic", "openai", "google")
        client_name: The client name for the error message (e.g., "AnthropicProvider")

    Returns:
        A callable that raises `ImportError` with helpful message.
    """

    def _raise_not_installed() -> None:
        raise ImportError(
            f"The '{package_name}' package is required to use {client_name}. "
            f"Install it with: `uv add 'mirascope[{package_name}]'`. "
            "Or use `uv add 'mirascope[all]'` to support all providers."
        )

    return _raise_not_installed


def create_provider_stub(
    package_name: str, provider_name: str
) -> type:  # pragma: no cover
    """Create a stub provider class that raises ImportError when instantiated.

    Args:
        package_name: The package/extra name (e.g., "anthropic", "openai", "google")
        provider_name: The client name for the error message (e.g., "AnthropicProvider")

    Returns:
        A stub class that raises `ImportError` on instantiation.
    """
    error_fn = create_import_error_stub(package_name, provider_name)

    class _ClientStub:
        """Stub client that raises `ImportError` when instantiated."""

        def __init__(self) -> None:
            error_fn()

    return _ClientStub
