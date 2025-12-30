"""OpenAI error handling utilities."""

from collections.abc import Generator
from contextlib import contextmanager

from openai import (
    AuthenticationError as OpenAIAuthenticationError,
    BadRequestError as OpenAIBadRequestError,
    RateLimitError as OpenAIRateLimitError,
)

from .....exceptions import AuthenticationError, NotFoundError, RateLimitError


def handle_openai_error(e: Exception) -> None:
    """Convert OpenAI errors to Mirascope errors.

    Args:
        e: The exception to handle.

    Raises:
        AuthenticationError: If the error is an authentication error (401).
        RateLimitError: If the error is a rate limit error.
        NotFoundError: If the error is a not found error (404 or 400 with model_not_found code).
        Exception: Re-raises the original exception if not handled.
    """
    if isinstance(e, OpenAIAuthenticationError):
        raise AuthenticationError(str(e)) from e
    if isinstance(e, OpenAIRateLimitError):
        raise RateLimitError(str(e)) from e
    # OpenAI Responses API returns 400 BadRequestError with code 'model_not_found'
    if (
        isinstance(e, OpenAIBadRequestError)
        and hasattr(e, "code")
        and e.code == "model_not_found"
    ):
        raise NotFoundError(str(e)) from e
    raise e  # pragma: no cover


@contextmanager
def wrap_openai_errors() -> Generator[None, None, None]:
    """Context manager that wraps OpenAI API errors.

    Usage:
        with wrap_openai_errors():
            response = client.responses.create(...)
    """
    try:
        yield
    except Exception as e:
        handle_openai_error(e)
