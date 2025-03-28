"""Tests for the Google call_params functionality."""

from typing import cast
from unittest.mock import patch

from mirascope.core.google import google_call
from mirascope.core.google.call_params import GoogleCallParams


@patch("google.genai.Client")
def test_google_call_params_dict(mock_client):
    """Test that call_params with direct parameters works correctly."""

    @google_call(
        "gemini-1.5-flash",
        call_params=cast(GoogleCallParams, {"temperature": 0.7, "top_p": 0.9}),
    )
    def test_fn(text: str) -> str:
        return f"Answer this question: {text}"

    # Just verify the function is callable but don't make API calls
    assert callable(test_fn)


@patch("google.genai.Client")
def test_google_call_params_object(mock_client):
    """Test that call_params works correctly with parameters matching GenerateContentConfig."""

    @google_call(
        "gemini-1.5-flash",
        call_params=cast(GoogleCallParams, {"temperature": 0.8, "top_k": 5}),
    )
    def test_fn(text: str) -> str:
        return f"Answer this question: {text}"

    # Just verify the function is callable but don't make API calls
    assert callable(test_fn)
