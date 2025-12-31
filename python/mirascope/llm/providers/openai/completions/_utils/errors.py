"""OpenAI error handling utilities."""

from collections.abc import Generator
from contextlib import contextmanager

from openai import (
    NotFoundError as OpenAINotFoundError,
    RateLimitError as OpenAIRateLimitError,
)

from .....exceptions import NotFoundError, RateLimitError


def handle_openai_error(e: Exception) -> None:
    """Convert OpenAI errors to Mirascope errors.

    Args:
        e: The exception to handle.

    Raises:
        RateLimitError: If the error is a rate limit error.
        NotFoundError: If the error is a not found error (404).
        Exception: Re-raises the original exception if not handled.
    """
    if isinstance(e, OpenAIRateLimitError):
        raise RateLimitError(str(e)) from e
    if isinstance(e, OpenAINotFoundError):
        raise NotFoundError(str(e)) from e
    raise e  # pragma: no cover


@contextmanager
def wrap_openai_errors() -> Generator[None, None, None]:
    """Context manager that wraps OpenAI API errors.

    Usage:
        with wrap_openai_errors():
            response = client.chat.completions.create(...)
    """
    try:
        yield
    except Exception as e:
        handle_openai_error(e)
