"""Mirascope llm exception hierarchy for unified error handling across providers."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .providers import ModelId, ProviderId


class Error(Exception):
    """Base exception for all Mirascope LLM errors."""


class ProviderError(Error):
    """Base class for errors that originate from a provider SDK.

    This wraps exceptions from provider libraries (OpenAI, Anthropic, etc.)
    and provides a unified interface for error handling.
    """

    provider: "ProviderId"
    """The provider that raised this error."""

    original_exception: Exception | None
    """The original exception from the provider SDK, if available."""

    def __init__(
        self,
        message: str,
        provider: "ProviderId",
        original_exception: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.original_exception = original_exception
        if original_exception is not None:
            self.__cause__ = original_exception


class APIError(ProviderError):
    """Base class for HTTP-level API errors."""

    status_code: int | None
    """The HTTP status code, if available."""

    def __init__(
        self,
        message: str,
        provider: "ProviderId",
        status_code: int | None = None,
        original_exception: Exception | None = None,
    ) -> None:
        super().__init__(message, provider, original_exception)
        self.status_code = status_code


class AuthenticationError(APIError):
    """Raised for authentication failures (401, invalid API keys)."""

    def __init__(
        self,
        message: str,
        provider: "ProviderId",
        status_code: int | None = None,
        original_exception: Exception | None = None,
    ) -> None:
        super().__init__(
            message,
            provider,
            status_code=status_code or 401,
            original_exception=original_exception,
        )


class PermissionError(APIError):
    """Raised for permission/authorization failures (403)."""

    def __init__(
        self,
        message: str,
        provider: "ProviderId",
        status_code: int | None = None,
        original_exception: Exception | None = None,
    ) -> None:
        super().__init__(
            message,
            provider,
            status_code=status_code or 403,
            original_exception=original_exception,
        )


class BadRequestError(APIError):
    """Raised for malformed requests (400, 422)."""

    def __init__(
        self,
        message: str,
        provider: "ProviderId",
        status_code: int | None = None,
        original_exception: Exception | None = None,
    ) -> None:
        super().__init__(
            message,
            provider,
            status_code=status_code or 400,
            original_exception=original_exception,
        )


class NotFoundError(APIError):
    """Raised when requested resource is not found (404)."""

    def __init__(
        self,
        message: str,
        provider: "ProviderId",
        status_code: int | None = None,
        original_exception: Exception | None = None,
    ) -> None:
        super().__init__(
            message,
            provider,
            status_code=status_code or 404,
            original_exception=original_exception,
        )


class RateLimitError(APIError):
    """Raised when rate limits are exceeded (429)."""

    def __init__(
        self,
        message: str,
        provider: "ProviderId",
        status_code: int | None = None,
        original_exception: Exception | None = None,
    ) -> None:
        super().__init__(
            message,
            provider,
            status_code=status_code or 429,
            original_exception=original_exception,
        )


class ServerError(APIError):
    """Raised for server-side errors (500+)."""

    def __init__(
        self,
        message: str,
        provider: "ProviderId",
        status_code: int | None = None,
        original_exception: Exception | None = None,
    ) -> None:
        super().__init__(
            message,
            provider,
            status_code=status_code or 500,
            original_exception=original_exception,
        )


class ConnectionError(ProviderError):
    """Raised when unable to connect to the API (network issues, timeouts)."""


class TimeoutError(ProviderError):
    """Raised when requests timeout or deadline exceeded."""


class ResponseValidationError(ProviderError):
    """Raised when API response fails validation.

    This wraps the APIResponseValidationErrors that OpenAI and Anthropic both return.
    """


class ToolNotFoundError(Error):
    """Raised if a tool_call cannot be converted to any corresponding tool."""


class FeatureNotSupportedError(Error):
    """Raised if a Mirascope feature is unsupported by chosen provider.

    If compatibility is model-specific, then `model_id` should be specified.
    If the feature is not supported by the provider at all, then it may be `None`.
    """

    provider_id: "ProviderId"
    model_id: "ModelId | None"
    feature: str

    def __init__(
        self,
        feature: str,
        provider_id: "ProviderId",
        model_id: "ModelId | None" = None,
        message: str | None = None,
    ) -> None:
        if message is None:
            model_msg = f" for model '{model_id}'" if model_id is not None else ""
            message = f"Feature '{feature}' is not supported by provider '{provider_id}'{model_msg}"
        super().__init__(message)
        self.feature = feature
        self.provider_id = provider_id
        self.model_id = model_id


class NoRegisteredProviderError(Error):
    """Raised when no provider is registered for a given model_id."""

    model_id: str

    def __init__(self, model_id: str) -> None:
        message = (
            f"No provider registered for model '{model_id}'. "
            f"Use llm.register_provider() to register a provider for this model."
        )
        super().__init__(message)
        self.model_id = model_id
