"""Tests for Anthropic error handling."""

from unittest.mock import MagicMock

import pytest
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

from mirascope.llm.exceptions import (
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
from mirascope.llm.providers.anthropic._utils.errors import handle_anthropic_error


def test_handle_authentication_error() -> None:
    """Test that AuthenticationError is properly wrapped."""
    anthropic_error = AnthropicAuthenticationError(
        "Invalid API key",
        response=MagicMock(status_code=401),
        body=None,
    )

    with pytest.raises(AuthenticationError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert "Invalid API key" in str(exc_info.value)
    assert exc_info.value.__cause__ is anthropic_error


def test_handle_permission_denied_error() -> None:
    """Test that PermissionDeniedError is properly wrapped."""
    anthropic_error = AnthropicPermissionDeniedError(
        "Permission denied",
        response=MagicMock(status_code=403),
        body=None,
    )

    with pytest.raises(PermissionError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert "Permission denied" in str(exc_info.value)
    assert exc_info.value.__cause__ is anthropic_error


def test_handle_bad_request_error() -> None:
    """Test that BadRequestError is properly wrapped."""
    anthropic_error = AnthropicBadRequestError(
        "Invalid request",
        response=MagicMock(status_code=400),
        body=None,
    )

    with pytest.raises(BadRequestError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert "Invalid request" in str(exc_info.value)
    assert exc_info.value.__cause__ is anthropic_error


def test_handle_unprocessable_entity_error() -> None:
    """Test that UnprocessableEntityError is wrapped as BadRequestError."""
    anthropic_error = AnthropicUnprocessableEntityError(
        "Unprocessable entity",
        response=MagicMock(status_code=422),
        body=None,
    )

    with pytest.raises(BadRequestError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert "Unprocessable entity" in str(exc_info.value)
    assert exc_info.value.__cause__ is anthropic_error


def test_handle_not_found_error() -> None:
    """Test that NotFoundError is properly wrapped."""
    anthropic_error = AnthropicNotFoundError(
        "Model not found",
        response=MagicMock(status_code=404),
        body=None,
    )

    with pytest.raises(NotFoundError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert "Model not found" in str(exc_info.value)
    assert exc_info.value.__cause__ is anthropic_error


def test_handle_conflict_error() -> None:
    """Test that ConflictError is wrapped as BadRequestError."""
    anthropic_error = AnthropicConflictError(
        "Conflict",
        response=MagicMock(status_code=409),
        body=None,
    )

    with pytest.raises(BadRequestError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert "Conflict" in str(exc_info.value)
    assert exc_info.value.__cause__ is anthropic_error


def test_handle_rate_limit_error() -> None:
    """Test that RateLimitError is properly wrapped."""
    anthropic_error = AnthropicRateLimitError(
        "Rate limit exceeded",
        response=MagicMock(status_code=429),
        body=None,
    )

    with pytest.raises(RateLimitError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert "Rate limit exceeded" in str(exc_info.value)
    assert exc_info.value.__cause__ is anthropic_error


def test_handle_internal_server_error() -> None:
    """Test that InternalServerError is wrapped as ServerError."""
    anthropic_error = AnthropicInternalServerError(
        "Internal server error",
        response=MagicMock(status_code=500),
        body=None,
    )

    with pytest.raises(ServerError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert "Internal server error" in str(exc_info.value)
    assert exc_info.value.__cause__ is anthropic_error


def test_handle_timeout_error() -> None:
    """Test that APITimeoutError is wrapped as TimeoutError."""
    anthropic_error = AnthropicAPITimeoutError(request=MagicMock())

    with pytest.raises(TimeoutError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert exc_info.value.__cause__ is anthropic_error


def test_handle_connection_error() -> None:
    """Test that APIConnectionError is wrapped as ConnectionError."""
    anthropic_error = AnthropicAPIConnectionError(
        message="Connection failed", request=MagicMock()
    )

    with pytest.raises(ConnectionError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert "Connection failed" in str(exc_info.value)
    assert exc_info.value.__cause__ is anthropic_error


def test_handle_validation_error() -> None:
    """Test that APIResponseValidationError is wrapped as ResponseValidationError."""
    mock_response = MagicMock()
    mock_response.request = MagicMock()
    mock_response.status_code = 200

    anthropic_error = AnthropicAPIResponseValidationError(
        response=mock_response,
        body=None,
        message="Validation failed",
    )

    with pytest.raises(ResponseValidationError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert "Validation failed" in str(exc_info.value)
    assert exc_info.value.__cause__ is anthropic_error


def test_handle_unknown_anthropic_error() -> None:
    """Test that unknown Anthropic SDK errors are wrapped as APIError."""
    # Create a generic AnthropicError (not a specific subclass)
    anthropic_error = AnthropicError("Unknown Anthropic error")

    with pytest.raises(APIError) as exc_info:
        handle_anthropic_error(anthropic_error)

    assert "Unknown Anthropic error" in str(exc_info.value)
    assert exc_info.value.__cause__ is anthropic_error


def test_handle_non_provider_error() -> None:
    """Test that non-Anthropic exceptions are re-raised as-is."""
    non_provider_error = ValueError("Some other error")

    with pytest.raises(ValueError) as exc_info:
        handle_anthropic_error(non_provider_error)

    assert exc_info.value is non_provider_error
