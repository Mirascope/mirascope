"""Mirascope exception hierarchy for unified error handling across providers."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import ModelId, Provider
    from .formatting import FormattingMode


class MirascopeError(Exception):
    """Base exception for all Mirascope errors."""

    original_exception: Exception | None


class APIError(MirascopeError):
    """Base class for API-related errors."""

    status_code: int | None


class ConnectionError(MirascopeError):
    """Raised when unable to connect to the API (network issues, timeouts)."""


class AuthenticationError(APIError):
    """Raised for authentication failures (401, invalid API keys)."""


class PermissionError(APIError):
    """Raised for permission/authorization failures (403)."""


class BadRequestError(APIError):
    """Raised for malformed requests (400, 422)."""


class NotFoundError(APIError):
    """Raised when requested resource is not found (404)."""


class ToolNotFoundError(MirascopeError):
    """Raised if a tool_call cannot be converted to any corresponding tool."""


class FeatureNotSupportedError(MirascopeError):
    """Raised if a Mirascope feature is unsupported by chosen provider and model."""

    provider: "Provider"
    model_id: "ModelId"

    def __init__(
        self,
        provider: "Provider",
        model_id: "ModelId",
    ) -> None:
        super().__init__()
        self.provider = provider
        self.model_id = model_id


class FormattingModeNotSupportedError(FeatureNotSupportedError):
    """Raised when trying to use a formatting mode that is not supported by the chosen model."""

    formatting_mode: "FormattingMode"

    def __init__(
        self,
        formatting_mode: "FormattingMode",
        provider: "Provider",
        model_id: "ModelId",
    ) -> None:
        super().__init__(provider=provider, model_id=model_id)
        self.formatting_mode = formatting_mode


class RateLimitError(APIError):
    """Raised when rate limits are exceeded (429)."""


class ServerError(APIError):
    """Raised for server-side errors (500+)."""


class TimeoutError(MirascopeError):
    """Raised when requests timeout or deadline exceeded."""
