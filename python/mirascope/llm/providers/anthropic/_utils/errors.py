"""Anthropic error handling utilities."""

from collections.abc import Generator
from contextlib import contextmanager

from anthropic import (
    AuthenticationError as AnthropicAuthenticationError,
    NotFoundError as AnthropicNotFoundError,
    RateLimitError as AnthropicRateLimitError,
)

from ....exceptions import AuthenticationError, NotFoundError, RateLimitError


def handle_anthropic_error(e: Exception) -> None:
    """Convert Anthropic errors to Mirascope errors.

    Args:
        e: The exception to handle.

    Raises:
        AuthenticationError: If the error is an authentication error (401).
        RateLimitError: If the error is a rate limit error.
        NotFoundError: If the error is a not found error (404).
        Exception: Re-raises the original exception if not handled.
    """
    if isinstance(e, AnthropicAuthenticationError):
        raise AuthenticationError(str(e)) from e
    if isinstance(e, AnthropicRateLimitError):
        raise RateLimitError(str(e)) from e
    if isinstance(e, AnthropicNotFoundError):
        raise NotFoundError(str(e)) from e
    raise e  # pragma: no cover


@contextmanager
def wrap_anthropic_errors() -> Generator[None, None, None]:
    """Context manager that wraps Anthropic API errors.

    Usage:
        with wrap_anthropic_errors():
            response = client.messages.create(...)
    """
    try:
        yield
    except Exception as e:
        handle_anthropic_error(e)
