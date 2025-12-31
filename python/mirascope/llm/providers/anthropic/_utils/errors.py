"""Anthropic error handling utilities."""

from collections.abc import Generator
from contextlib import contextmanager

from anthropic import (
    AnthropicError,
    APIConnectionError as AnthropicAPIConnectionError,
    APIResponseValidationError as AnthropicAPIResponseValidationError,
    APITimeoutError as AnthropicAPITimeoutError,
    AuthenticationError as AnthropicAuthenticationError,
    BadRequestError as AnthropicBadRequestError,
    ConflictError as AnthropicConflictError,
    InternalServerError as AnthropicInternalServerError,
    NotFoundError as AnthropicNotFoundError,
    PermissionDeniedError as AnthropicPermissionDeniedError,
    RateLimitError as AnthropicRateLimitError,
    UnprocessableEntityError as AnthropicUnprocessableEntityError,
)

from ....exceptions import (
    APIError,
    AuthenticationError,
    BadRequestError,
    ConnectionError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ResponseValidationError,
    ServerError,
    TimeoutError,
)


def handle_anthropic_error(e: Exception) -> None:
    """Convert Anthropic errors to Mirascope errors.

    Args:
        e: The exception to handle.

    Raises:
        AuthenticationError: If the error is an authentication error (401).
        PermissionError: If the error is a permission denied error (403).
        BadRequestError: If the error is a bad request error (400, 422).
        NotFoundError: If the error is a not found error (404).
        RateLimitError: If the error is a rate limit error (429).
        ServerError: If the error is a server error (500+).
        TimeoutError: If the error is a timeout error.
        ConnectionError: If the error is a connection error.
        ResponseValidationError: If the API response fails validation.
        APIError: For unknown Anthropic SDK errors that cannot be mapped.
        Exception: Re-raises the original exception if not from Anthropic SDK.
    """
    # Authentication errors (401)
    if isinstance(e, AnthropicAuthenticationError):
        raise AuthenticationError(str(e)) from e

    # Permission errors (403)
    if isinstance(e, AnthropicPermissionDeniedError):
        raise PermissionError(str(e)) from e

    # Bad request errors (400, 422)
    if isinstance(e, AnthropicBadRequestError | AnthropicUnprocessableEntityError):
        raise BadRequestError(str(e)) from e

    # Not found errors (404)
    if isinstance(e, AnthropicNotFoundError):
        raise NotFoundError(str(e)) from e

    # Conflict errors (409) - treat as bad request
    if isinstance(e, AnthropicConflictError):
        raise BadRequestError(str(e)) from e

    # Rate limit errors (429)
    if isinstance(e, AnthropicRateLimitError):
        raise RateLimitError(str(e)) from e

    # Server errors (500+)
    if isinstance(e, AnthropicInternalServerError):
        raise ServerError(str(e)) from e

    # Timeout errors
    if isinstance(e, AnthropicAPITimeoutError):
        raise TimeoutError(str(e)) from e

    # Connection errors
    if isinstance(e, AnthropicAPIConnectionError):
        raise ConnectionError(str(e)) from e

    # Validation errors
    if isinstance(e, AnthropicAPIResponseValidationError):
        raise ResponseValidationError(str(e)) from e

    # Unknown Anthropic SDK errors - wrap as generic APIError
    if isinstance(e, AnthropicError):
        raise APIError(str(e)) from e

    # Non-Anthropic errors - re-raise as-is
    raise e


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
