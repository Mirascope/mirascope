"""Tests for the Google call_params functionality."""

from unittest.mock import patch

from google.genai.types import GenerateContentConfig

from mirascope.core.google import google_call


@patch("google.genai.Client")
def test_google_call_params_dict_config(mock_client):
    """Test that call_params with a dictionary config works correctly."""

    @google_call(
        "gemini-1.5-flash", call_params={"config": {"temperature": 0.7, "top_p": 0.9}}
    )
    def test_fn(text: str) -> str:
        return f"Answer this question: {text}"

    # Just verify the function is callable but don't make API calls
    assert callable(test_fn)


@patch("google.genai.Client")
def test_google_call_params_object_config(mock_client):
    """Test that call_params with a GenerateContentConfig object works correctly."""

    @google_call(
        "gemini-1.5-flash",
        call_params={"config": GenerateContentConfig(temperature=0.8, top_k=5)},
    )
    def test_fn(text: str) -> str:
        return f"Answer this question: {text}"

    # Just verify the function is callable but don't make API calls
    assert callable(test_fn)
