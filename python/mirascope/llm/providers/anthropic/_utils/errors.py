"""Anthropic error handling utilities."""

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
    AuthenticationError,
    BadRequestError,
    ConnectionError,
    NotFoundError,
    PermissionError,
    ProviderError,
    RateLimitError,
    ResponseValidationError,
    ServerError,
    TimeoutError,
)
from ...base import ProviderErrorMap

# Shared error mapping used by both AnthropicProvider and AnthropicBetaProvider
ANTHROPIC_ERROR_MAP: ProviderErrorMap = {
    AnthropicAuthenticationError: AuthenticationError,
    AnthropicPermissionDeniedError: PermissionError,
    AnthropicBadRequestError: BadRequestError,
    AnthropicUnprocessableEntityError: BadRequestError,
    AnthropicNotFoundError: NotFoundError,
    AnthropicConflictError: BadRequestError,
    AnthropicRateLimitError: RateLimitError,
    AnthropicInternalServerError: ServerError,
    AnthropicAPITimeoutError: TimeoutError,
    AnthropicAPIConnectionError: ConnectionError,
    AnthropicAPIResponseValidationError: ResponseValidationError,
    AnthropicError: ProviderError,  # Catch-all for unknown Anthropic errors
}
