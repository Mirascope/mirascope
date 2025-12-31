"""OpenAI error handling utilities."""

from collections.abc import Generator
from contextlib import contextmanager

from openai import (
    APIConnectionError as OpenAIAPIConnectionError,
    APIResponseValidationError as OpenAIAPIResponseValidationError,
    APITimeoutError as OpenAIAPITimeoutError,
    AuthenticationError as OpenAIAuthenticationError,
    BadRequestError as OpenAIBadRequestError,
    ConflictError as OpenAIConflictError,
    InternalServerError as OpenAIInternalServerError,
    NotFoundError as OpenAINotFoundError,
    OpenAIError,
    PermissionDeniedError as OpenAIPermissionDeniedError,
    RateLimitError as OpenAIRateLimitError,
    UnprocessableEntityError as OpenAIUnprocessableEntityError,
)

from .....exceptions import (
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


def handle_openai_error(e: Exception) -> None:
    """Convert OpenAI errors to Mirascope errors.

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
        APIError: For unknown OpenAI SDK errors that cannot be mapped.
        Exception: Re-raises the original exception if not from OpenAI SDK.
    """
    # Authentication errors (401)
    if isinstance(e, OpenAIAuthenticationError):
        error = AuthenticationError(str(e), status_code=getattr(e, "status_code", None))
        error.original_exception = e
        raise error from e

    # Permission errors (403)
    if isinstance(e, OpenAIPermissionDeniedError):
        error = PermissionError(str(e), status_code=getattr(e, "status_code", None))
        error.original_exception = e
        raise error from e

    # Bad request errors (400, 422)
    if isinstance(e, OpenAIBadRequestError | OpenAIUnprocessableEntityError):
        error = BadRequestError(str(e), status_code=getattr(e, "status_code", None))
        error.original_exception = e
        raise error from e

    # Not found errors (404)
    if isinstance(e, OpenAINotFoundError):
        error = NotFoundError(str(e), status_code=getattr(e, "status_code", None))
        error.original_exception = e
        raise error from e

    # Conflict errors (409) - treat as bad request
    if isinstance(e, OpenAIConflictError):
        error = BadRequestError(str(e), status_code=getattr(e, "status_code", None))
        error.original_exception = e
        raise error from e

    # Rate limit errors (429)
    if isinstance(e, OpenAIRateLimitError):
        error = RateLimitError(str(e), status_code=getattr(e, "status_code", None))
        error.original_exception = e
        raise error from e

    # Server errors (500+)
    if isinstance(e, OpenAIInternalServerError):
        error = ServerError(str(e), status_code=getattr(e, "status_code", None))
        error.original_exception = e
        raise error from e

    # Timeout errors
    if isinstance(e, OpenAIAPITimeoutError):
        raise TimeoutError(str(e)) from e

    # Connection errors
    if isinstance(e, OpenAIAPIConnectionError):
        raise ConnectionError(str(e)) from e

    # Validation errors
    if isinstance(e, OpenAIAPIResponseValidationError):
        raise ResponseValidationError(str(e)) from e

    # Unknown OpenAI SDK errors - wrap as generic APIError
    if isinstance(e, OpenAIError):
        error = APIError(str(e), status_code=getattr(e, "status_code", None))
        error.original_exception = e
        raise error from e

    # Non-OpenAI errors - re-raise as-is
    raise e


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
