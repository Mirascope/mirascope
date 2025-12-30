"""Tests for Google error handling."""

from unittest.mock import MagicMock

import pytest
from google.genai.errors import (
    ClientError as GoogleClientError,
    ServerError as GoogleServerError,
)

from mirascope.llm.exceptions import (
    APIError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
)
from mirascope.llm.providers.google._utils.errors import handle_google_error


def test_handle_authentication_error_401() -> None:
    """Test that 401 errors are wrapped as AuthenticationError."""
    google_error = GoogleClientError(
        code=401,
        response_json={
            "error": {"message": "Unauthorized", "status": "UNAUTHENTICATED"}
        },
        response=MagicMock(),
    )

    with pytest.raises(AuthenticationError) as exc_info:
        handle_google_error(google_error)

    assert exc_info.value.__cause__ is google_error


def test_handle_authentication_error_invalid_api_key() -> None:
    """Test that 400 with 'API key not valid' is wrapped as AuthenticationError."""
    google_error = GoogleClientError(
        code=400,
        response_json={
            "error": {"message": "API key not valid. Please pass a valid API key."}
        },
        response=MagicMock(),
    )

    with pytest.raises(AuthenticationError) as exc_info:
        handle_google_error(google_error)

    assert "API key not valid" in str(exc_info.value)
    assert exc_info.value.__cause__ is google_error


def test_handle_permission_denied_error() -> None:
    """Test that 403 errors are wrapped as PermissionError."""
    google_error = GoogleClientError(
        code=403,
        response_json={
            "error": {"message": "Permission denied", "status": "PERMISSION_DENIED"}
        },
        response=MagicMock(),
    )

    with pytest.raises(PermissionError) as exc_info:
        handle_google_error(google_error)

    assert exc_info.value.__cause__ is google_error


def test_handle_not_found_error() -> None:
    """Test that 404 errors are wrapped as NotFoundError."""
    google_error = GoogleClientError(
        code=404,
        response_json={"error": {"message": "Model not found", "status": "NOT_FOUND"}},
        response=MagicMock(),
    )

    with pytest.raises(NotFoundError) as exc_info:
        handle_google_error(google_error)

    assert exc_info.value.__cause__ is google_error


def test_handle_rate_limit_error() -> None:
    """Test that 429 errors are wrapped as RateLimitError."""
    google_error = GoogleServerError(
        code=429,
        response_json={
            "error": {
                "message": "Resource has been exhausted",
                "status": "RESOURCE_EXHAUSTED",
            }
        },
        response=MagicMock(),
    )

    with pytest.raises(RateLimitError) as exc_info:
        handle_google_error(google_error)

    assert exc_info.value.__cause__ is google_error


def test_handle_bad_request_error_400() -> None:
    """Test that 400 errors (not auth) are wrapped as BadRequestError."""
    google_error = GoogleClientError(
        code=400,
        response_json={
            "error": {"message": "Invalid argument", "status": "INVALID_ARGUMENT"}
        },
        response=MagicMock(),
    )

    with pytest.raises(BadRequestError) as exc_info:
        handle_google_error(google_error)

    assert exc_info.value.__cause__ is google_error


def test_handle_bad_request_error_422() -> None:
    """Test that 422 errors are wrapped as BadRequestError."""
    google_error = GoogleClientError(
        code=422,
        response_json={
            "error": {"message": "Unprocessable entity", "status": "UNPROCESSABLE"}
        },
        response=MagicMock(),
    )

    with pytest.raises(BadRequestError) as exc_info:
        handle_google_error(google_error)

    assert exc_info.value.__cause__ is google_error


def test_handle_server_error_500() -> None:
    """Test that 500 errors are wrapped as ServerError."""
    google_error = GoogleServerError(
        code=500,
        response_json={"error": {"message": "Internal error", "status": "INTERNAL"}},
        response=MagicMock(),
    )

    with pytest.raises(ServerError) as exc_info:
        handle_google_error(google_error)

    assert exc_info.value.__cause__ is google_error


def test_handle_server_error_503() -> None:
    """Test that 503 errors are wrapped as ServerError."""
    google_error = GoogleServerError(
        code=503,
        response_json={
            "error": {"message": "Service unavailable", "status": "UNAVAILABLE"}
        },
        response=MagicMock(),
    )

    with pytest.raises(ServerError) as exc_info:
        handle_google_error(google_error)

    assert exc_info.value.__cause__ is google_error


def test_handle_unknown_client_error() -> None:
    """Test that unknown client errors (e.g., 409, 410) are wrapped as APIError."""
    google_error = GoogleClientError(
        code=409,
        response_json={"error": {"message": "Conflict", "status": "CONFLICT"}},
        response=MagicMock(),
    )

    with pytest.raises(APIError) as exc_info:
        handle_google_error(google_error)

    assert exc_info.value.__cause__ is google_error


def test_handle_unknown_server_error() -> None:
    """Test that unknown server errors are wrapped as APIError."""
    google_error = GoogleServerError(
        code=499,  # Non-standard code
        response_json={"error": {"message": "Unknown error", "status": "UNKNOWN"}},
        response=MagicMock(),
    )

    with pytest.raises(APIError) as exc_info:
        handle_google_error(google_error)

    assert exc_info.value.__cause__ is google_error


def test_handle_unknown_error() -> None:
    """Test that non-Google exceptions are re-raised as-is."""
    unknown_error = ValueError("Some other error")

    with pytest.raises(ValueError) as exc_info:
        handle_google_error(unknown_error)

    assert exc_info.value is unknown_error
