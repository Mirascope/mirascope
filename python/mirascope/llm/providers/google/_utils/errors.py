"""Google error handling utilities."""

from collections.abc import Generator
from contextlib import contextmanager

from google.genai.errors import (
    ClientError as GoogleClientError,
    ServerError as GoogleServerError,
)

from ....exceptions import (
    APIError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
)


def handle_google_error(e: Exception) -> None:
    """Convert Google errors to Mirascope errors.

    Note: Google's error system only provides ClientError (4xx) and ServerError (5xx)
    with HTTP status codes. We do best-effort mapping based on status codes and
    error message patterns.

    Args:
        e: The exception to handle.

    Raises:
        AuthenticationError: If the error is an authentication error (401).
        PermissionError: If the error is a permission denied error (403).
        BadRequestError: If the error is a bad request error (400, 422).
        NotFoundError: If the error is a not found error (404).
        RateLimitError: If the error is a rate limit error (429).
        ServerError: If the error is a server error (500+).
        APIError: If the error cannot be mapped to a specific error type.
        Exception: Re-raises the original exception if not handled.
    """
    if not isinstance(e, GoogleClientError | GoogleServerError):
        raise e  # pragma: no cover

    # Authentication errors (401)
    # Also check for 400 with "API key not valid" message (Google's pattern)
    if e.code == 401 or (e.code == 400 and "API key not valid" in str(e)):
        raise AuthenticationError(str(e)) from e

    # Permission errors (403)
    if e.code == 403:
        raise PermissionError(str(e)) from e

    # Not found errors (404)
    if e.code == 404:
        raise NotFoundError(str(e)) from e

    # Rate limit errors (429)
    if e.code == 429:
        raise RateLimitError(str(e)) from e

    # Bad request errors (400, 422)
    if e.code in (400, 422):
        raise BadRequestError(str(e)) from e

    # Server errors (500+) - map known ones to ServerError
    if isinstance(e, GoogleServerError) and e.code >= 500:
        raise ServerError(str(e)) from e

    # Unknown errors - wrap as generic APIError to preserve information
    raise APIError(str(e)) from e


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
