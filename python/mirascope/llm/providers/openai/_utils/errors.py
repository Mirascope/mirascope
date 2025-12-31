"""OpenAI error handling utilities."""

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
from ...base import ProviderErrorMap

# Shared error mapping used by OpenAI Responses and Completions providers
OPENAI_ERROR_MAP: ProviderErrorMap = {
    OpenAIAuthenticationError: AuthenticationError,
    OpenAIPermissionDeniedError: PermissionError,
    OpenAINotFoundError: NotFoundError,
    OpenAIBadRequestError: BadRequestError,
    OpenAIUnprocessableEntityError: BadRequestError,
    OpenAIConflictError: BadRequestError,
    OpenAIRateLimitError: RateLimitError,
    OpenAIInternalServerError: ServerError,
    OpenAIAPITimeoutError: TimeoutError,
    OpenAIAPIConnectionError: ConnectionError,
    OpenAIAPIResponseValidationError: ResponseValidationError,
    OpenAIError: APIError,  # Catch-all for unknown OpenAI errors
}
