"""Mirascope llm exception hierarchy for unified error handling across providers."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import ModelId, Provider
    from .formatting import FormattingMode


class MirascopeLLMError(Exception):
    """Base exception for all Mirascope LLM errors."""

    original_exception: Exception | None


class APIError(MirascopeLLMError):
    """Base class for API-related errors."""

    status_code: int | None


class ConnectionError(MirascopeLLMError):
    """Raised when unable to connect to the API (network issues, timeouts)."""


class AuthenticationError(APIError):
    """Raised for authentication failures (401, invalid API keys)."""


class PermissionError(APIError):
    """Raised for permission/authorization failures (403)."""


class BadRequestError(APIError):
    """Raised for malformed requests (400, 422)."""


class NotFoundError(APIError):
    """Raised when requested resource is not found (404)."""


class ToolNotFoundError(MirascopeLLMError):
    """Raised if a tool_call cannot be converted to any corresponding tool."""


class FeatureNotSupportedError(MirascopeLLMError):
    """Raised if a Mirascope feature is unsupported by chosen provider.

    If compatibility is model-specific, then `model_id` should be specified.
    If the feature is not supported by the provider at all, then it may be `None`."""

    provider: "Provider"
    model_id: "ModelId | None"
    feature: str

    def __init__(
        self,
        feature: str,
        provider: "Provider",
        model_id: "ModelId | None" = None,
        message: str | None = None,
    ) -> None:
        if message is None:
            model_msg = f" for model '{model_id}'" if model_id is not None else ""
            message = f"Feature '{feature}' is not supported by provider '{provider}'{model_msg}"
        super().__init__(message)
        self.feature = feature
        self.provider = provider
        self.model_id = model_id


class FormattingModeNotSupportedError(FeatureNotSupportedError):
    """Raised when trying to use a formatting mode that is not supported by the chosen model."""

    formatting_mode: "FormattingMode"

    def __init__(
        self,
        formatting_mode: "FormattingMode",
        provider: "Provider",
        model_id: "ModelId | None" = None,
        message: str | None = None,
    ) -> None:
        if message is None:
            model_msg = f" for model '{model_id}'" if model_id is not None else ""
            message = f"Formatting mode '{formatting_mode}' is not supported by provider '{provider}'{model_msg}"
        super().__init__(
            feature=f"formatting_mode:{formatting_mode}",
            provider=provider,
            model_id=model_id,
            message=message,
        )
        self.formatting_mode = formatting_mode


class RateLimitError(APIError):
    """Raised when rate limits are exceeded (429)."""


class ServerError(APIError):
    """Raised for server-side errors (500+)."""


class TimeoutError(MirascopeLLMError):
    """Raised when requests timeout or deadline exceeded."""
