"""Google error handling utilities."""

from collections.abc import Generator
from contextlib import contextmanager

from google.genai.errors import (
    ClientError as GoogleClientError,
    ServerError as GoogleServerError,
)

from ....exceptions import NotFoundError, RateLimitError


def handle_google_error(e: Exception) -> None:
    """Convert Google errors to Mirascope errors.

    Args:
        e: The exception to handle.

    Raises:
        RateLimitError: If the error is a rate limit error (HTTP 429).
        NotFoundError: If the error is a not found error (HTTP 404).
        Exception: Re-raises the original exception if not handled.
    """
    # Google uses HTTP 429 for rate limit errors (RESOURCE_EXHAUSTED)
    # The error code is stored in the .code attribute
    if isinstance(e, GoogleServerError) and e.code == 429:
        raise RateLimitError(str(e)) from e
    # Google uses HTTP 404 for not found errors (NOT_FOUND)
    if isinstance(e, GoogleClientError) and e.code == 404:
        raise NotFoundError(str(e)) from e
    raise e  # pragma: no cover


@contextmanager
def wrap_google_errors() -> Generator[None, None, None]:
    """Context manager that wraps Google API errors.

    Usage:
        with wrap_google_errors():
            response = client.models.generate_content(...)
    """
    try:
        yield
    except Exception as e:
        handle_google_error(e)
