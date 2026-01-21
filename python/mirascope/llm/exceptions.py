"""Mirascope llm exception hierarchy for unified error handling across providers."""

import json
from typing import TYPE_CHECKING

from pydantic import ValidationError

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


class ToolError(Error):
    """Base class for errors that occur during tool execution."""


class ToolExecutionError(ToolError):
    """Raised if an uncaught exception is thrown while executing a tool."""

    tool_exception: Exception
    """The exception that was thrown while executing the tool."""

    def __init__(self, tool_exception: Exception | str) -> None:
        if isinstance(tool_exception, str):
            # Support string for snapshot reconstruction
            message = tool_exception
            tool_exception = ValueError(message)
        else:
            message = str(tool_exception)
        super().__init__(message)
        self.tool_exception = tool_exception
        self.__cause__ = tool_exception

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ToolExecutionError):
            return False
        # Needed for snapshot tests.
        return str(self) == str(other)


class ToolNotFoundError(ToolError):
    """Raised if a tool call does not match any registered tool."""

    tool_name: str
    """The name of the tool that was not found."""

    def __init__(self, tool_name: str) -> None:
        super().__init__(f"Tool '{tool_name}' not found in registered tools")
        self.tool_name = tool_name

    def __repr__(self) -> str:
        return f"ToolNotFoundError({self.tool_name!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ToolNotFoundError):
            return NotImplemented
        return self.tool_name == other.tool_name

    def __hash__(self) -> int:
        return hash((type(self), self.tool_name))


class ParseError(Error):
    """Raised when response.parse() fails to parse the response content.

    This wraps errors from JSON extraction, JSON parsing, Pydantic validation,
    or custom OutputParser functions.
    """

    original_exception: Exception
    """The original exception that caused the parse failure."""

    def __init__(
        self,
        message: str,
        original_exception: Exception,
    ) -> None:
        super().__init__(message)
        self.original_exception = original_exception
        self.__cause__ = original_exception

    def retry_message(self) -> str:
        """Generate a message suitable for retrying with the LLM.

        Returns a user-friendly message describing what went wrong,
        suitable for including in a retry prompt.
        """

        if isinstance(self.original_exception, ValidationError):
            return (
                f"Your response failed schema validation:\n"
                f"{self.original_exception}\n\n"
                "Please correct these issues and respond again."
            )
        elif isinstance(self.original_exception, json.JSONDecodeError):
            # JSON syntax error
            return (
                "Your response could not be parsed because no valid JSON object "
                "was found. Please ensure your response contains a JSON object "
                "with opening '{' and closing '}' braces."
            )
        else:
            # ValueError from JSON extraction, or OutputParser error
            return (
                f"Your response could not be parsed: {self.original_exception}\n\n"
                "Please ensure your response matches the expected format."
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ParseError):
            return False
        return str(self) == str(other)


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


class MissingAPIKeyError(Error):
    """Raised when no API key is available for a provider.

    This error is raised during auto-registration when the required API key
    environment variable is not set. If a Mirascope fallback is available,
    the error message will suggest using MIRASCOPE_API_KEY as an alternative.
    """

    provider_id: str
    """The provider that requires an API key."""

    env_var: str
    """The environment variable that should contain the API key."""

    def __init__(
        self,
        provider_id: str,
        env_var: str,
        has_mirascope_fallback: bool = False,
    ) -> None:
        if has_mirascope_fallback:
            message = (
                f"No API key found for {provider_id}. Either:\n"
                f"  1. Set {env_var} environment variable, or\n"
                f"  2. Set MIRASCOPE_API_KEY for cross-provider support "
                f"via Mirascope Router\n"
                f"     (Learn more: https://mirascope.com/docs/router)"
            )
        else:
            message = (
                f"No API key found for {provider_id}. "
                f"Set the {env_var} environment variable."
            )
        super().__init__(message)
        self.provider_id = provider_id
        self.env_var = env_var
