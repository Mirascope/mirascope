"""Tests for OpenAI responses error handling."""

from unittest.mock import MagicMock

import pytest
from openai import (
    APIConnectionError as OpenAIAPIConnectionError,
    APIResponseValidationError as OpenAIAPIResponseValidationError,
    APITimeoutError as OpenAIAPITimeoutError,
    AuthenticationError as OpenAIAuthenticationError,
    BadRequestError as OpenAIBadRequestError,
    ConflictError as OpenAIConflictError,
    InternalServerError as OpenAIInternalServerError,
    NotFoundError as OpenAINotFoundError,
    PermissionDeniedError as OpenAIPermissionDeniedError,
    RateLimitError as OpenAIRateLimitError,
    UnprocessableEntityError as OpenAIUnprocessableEntityError,
)

from mirascope.llm.exceptions import (
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
from mirascope.llm.providers.openai.responses._utils.errors import (
    handle_openai_error,
)


def test_handle_authentication_error() -> None:
    """Test that AuthenticationError is properly wrapped."""
    openai_error = OpenAIAuthenticationError(
        "Invalid API key",
        response=MagicMock(status_code=401),
        body=None,
    )

    with pytest.raises(AuthenticationError) as exc_info:
        handle_openai_error(openai_error)

    assert "Invalid API key" in str(exc_info.value)
    assert exc_info.value.__cause__ is openai_error


def test_handle_permission_denied_error() -> None:
    """Test that PermissionDeniedError is properly wrapped."""
    openai_error = OpenAIPermissionDeniedError(
        "Permission denied",
        response=MagicMock(status_code=403),
        body=None,
    )

    with pytest.raises(PermissionError) as exc_info:
        handle_openai_error(openai_error)

    assert "Permission denied" in str(exc_info.value)
    assert exc_info.value.__cause__ is openai_error


def test_handle_bad_request_error() -> None:
    """Test that BadRequestError is properly wrapped."""
    openai_error = OpenAIBadRequestError(
        "Invalid request",
        response=MagicMock(status_code=400),
        body=None,
    )

    with pytest.raises(BadRequestError) as exc_info:
        handle_openai_error(openai_error)

    assert "Invalid request" in str(exc_info.value)
    assert exc_info.value.__cause__ is openai_error


def test_handle_bad_request_with_model_not_found() -> None:
    """Test that BadRequestError with model_not_found code is wrapped as NotFoundError."""
    openai_error = OpenAIBadRequestError(
        "Model not found",
        response=MagicMock(status_code=400),
        body=None,
    )
    openai_error.code = "model_not_found"

    with pytest.raises(NotFoundError) as exc_info:
        handle_openai_error(openai_error)

    assert "Model not found" in str(exc_info.value)
    assert exc_info.value.__cause__ is openai_error


def test_handle_unprocessable_entity_error() -> None:
    """Test that UnprocessableEntityError is wrapped as BadRequestError."""
    openai_error = OpenAIUnprocessableEntityError(
        "Unprocessable entity",
        response=MagicMock(status_code=422),
        body=None,
    )

    with pytest.raises(BadRequestError) as exc_info:
        handle_openai_error(openai_error)

    assert "Unprocessable entity" in str(exc_info.value)
    assert exc_info.value.__cause__ is openai_error


def test_handle_not_found_error() -> None:
    """Test that NotFoundError is properly wrapped."""
    openai_error = OpenAINotFoundError(
        "Model not found",
        response=MagicMock(status_code=404),
        body=None,
    )

    with pytest.raises(NotFoundError) as exc_info:
        handle_openai_error(openai_error)

    assert "Model not found" in str(exc_info.value)
    assert exc_info.value.__cause__ is openai_error


def test_handle_conflict_error() -> None:
    """Test that ConflictError is wrapped as BadRequestError."""
    openai_error = OpenAIConflictError(
        "Conflict",
        response=MagicMock(status_code=409),
        body=None,
    )

    with pytest.raises(BadRequestError) as exc_info:
        handle_openai_error(openai_error)

    assert "Conflict" in str(exc_info.value)
    assert exc_info.value.__cause__ is openai_error


def test_handle_rate_limit_error() -> None:
    """Test that RateLimitError is properly wrapped."""
    openai_error = OpenAIRateLimitError(
        "Rate limit exceeded",
        response=MagicMock(status_code=429),
        body=None,
    )

    with pytest.raises(RateLimitError) as exc_info:
        handle_openai_error(openai_error)

    assert "Rate limit exceeded" in str(exc_info.value)
    assert exc_info.value.__cause__ is openai_error


def test_handle_internal_server_error() -> None:
    """Test that InternalServerError is wrapped as ServerError."""
    openai_error = OpenAIInternalServerError(
        "Internal server error",
        response=MagicMock(status_code=500),
        body=None,
    )

    with pytest.raises(ServerError) as exc_info:
        handle_openai_error(openai_error)

    assert "Internal server error" in str(exc_info.value)
    assert exc_info.value.__cause__ is openai_error


def test_handle_timeout_error() -> None:
    """Test that APITimeoutError is wrapped as TimeoutError."""
    openai_error = OpenAIAPITimeoutError(request=MagicMock())

    with pytest.raises(TimeoutError) as exc_info:
        handle_openai_error(openai_error)

    assert exc_info.value.__cause__ is openai_error


def test_handle_connection_error() -> None:
    """Test that APIConnectionError is wrapped as ConnectionError."""
    openai_error = OpenAIAPIConnectionError(
        message="Connection failed", request=MagicMock()
    )

    with pytest.raises(ConnectionError) as exc_info:
        handle_openai_error(openai_error)

    assert "Connection failed" in str(exc_info.value)
    assert exc_info.value.__cause__ is openai_error


def test_handle_validation_error() -> None:
    """Test that APIResponseValidationError is wrapped as ResponseValidationError."""
    mock_response = MagicMock()
    mock_response.request = MagicMock()
    mock_response.status_code = 200

    openai_error = OpenAIAPIResponseValidationError(
        response=mock_response,
        body=None,
        message="Validation failed",
    )

    with pytest.raises(ResponseValidationError) as exc_info:
        handle_openai_error(openai_error)

    assert "Validation failed" in str(exc_info.value)
    assert exc_info.value.__cause__ is openai_error


def test_handle_unknown_error() -> None:
    """Test that unknown exceptions are re-raised as-is."""
    unknown_error = ValueError("Some other error")

    with pytest.raises(ValueError) as exc_info:
        handle_openai_error(unknown_error)

    assert exc_info.value is unknown_error
