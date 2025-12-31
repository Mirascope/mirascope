"""Tests for error wrapping and status code extraction."""

from unittest.mock import Mock

from mirascope.llm.exceptions import (
    BadRequestError,
    PermissionError,
    ServerError,
)


def test_openai_completions_get_error_status() -> None:
    """Test that OpenAI Completions provider extracts status codes from errors."""
    from mirascope.llm.providers.openai.completions.base_provider import (
        BaseOpenAICompletionsProvider,
    )

    # We can't instantiate the base class directly, so we'll test via mock
    provider = Mock(spec=BaseOpenAICompletionsProvider)

    # Create mock error with status_code attribute
    mock_error = Mock()
    mock_error.status_code = 429

    # Call the real method
    status = BaseOpenAICompletionsProvider.get_error_status(provider, mock_error)
    assert status == 429

    # Test with error without status_code
    mock_error_no_status = Mock(spec=[])
    status_none = BaseOpenAICompletionsProvider.get_error_status(
        provider, mock_error_no_status
    )
    assert status_none is None


def test_openai_responses_get_error_status() -> None:
    """Test that OpenAI Responses provider extracts status codes from errors."""
    from mirascope.llm.providers.openai.responses.provider import (
        OpenAIResponsesProvider,
    )

    provider = OpenAIResponsesProvider(api_key="test")

    # Create mock error with status_code attribute
    mock_error = Mock()
    mock_error.status_code = 500
    assert provider.get_error_status(mock_error) == 500

    # Test with error without status_code
    mock_error_no_status = Mock(spec=[])
    assert provider.get_error_status(mock_error_no_status) is None


def test_permission_error_without_status_code() -> None:
    """Test PermissionError uses default 403 when status_code is None."""
    error = PermissionError("Permission denied", status_code=None)
    assert error.status_code == 403


def test_bad_request_error_without_status_code() -> None:
    """Test BadRequestError uses default 400 when status_code is None."""
    error = BadRequestError("Bad request", status_code=None)
    assert error.status_code == 400


def test_server_error_without_status_code() -> None:
    """Test ServerError uses default 500 when status_code is None."""
    error = ServerError("Server error", status_code=None)
    assert error.status_code == 500
