"""Google error handling utilities."""

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
    ProviderError,
    RateLimitError,
    ServerError,
)
from ...base import ProviderErrorMap


def map_google_error(e: Exception) -> type[ProviderError]:
    """Map Google error to appropriate Mirascope error type.

    Google only provides ClientError (4xx) and ServerError (5xx) with status codes,
    so we map based on status code and message patterns.
    """
    if not isinstance(e, GoogleClientError | GoogleServerError):
        return ProviderError

    # Authentication errors (401) or 400 with "API key not valid"
    if e.code == 401 or (e.code == 400 and "API key not valid" in str(e)):
        return AuthenticationError
    if e.code == 403:
        return PermissionError
    if e.code == 404:
        return NotFoundError
    if e.code == 429:
        return RateLimitError
    if e.code in (400, 422):
        return BadRequestError
    if isinstance(e, GoogleServerError) and e.code >= 500:
        return ServerError
    return APIError


# Shared error mapping for Google provider
GOOGLE_ERROR_MAP: ProviderErrorMap = {
    GoogleClientError: map_google_error,
    GoogleServerError: map_google_error,
}
