"""Tests for llm.clients.GoogleClient."""

from unittest.mock import MagicMock, patch

from mirascope import llm


def test_custom_base_url() -> None:
    """Test that custom base URL is used for API requests."""
    example_url = "https://example.com"

    with patch("mirascope.llm.clients.google.clients.Client") as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        google_client = llm.client("google", base_url=example_url)

        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        assert call_args.kwargs["http_options"] is not None
        assert call_args.kwargs["http_options"].base_url == example_url

        assert google_client.client is mock_client_instance


def test_client_caching() -> None:
    """Test that client() returns cached instances for identical parameters."""
    client1 = llm.client(
        "google", api_key="test-key", base_url="https://api.example.com"
    )
    client2 = llm.client(
        "google", api_key="test-key", base_url="https://api.example.com"
    )
    assert client1 is client2

    client3 = llm.client(
        "google", api_key="different-key", base_url="https://api.example.com"
    )
    assert client1 is not client3

    client4 = llm.client(
        "google", api_key="test-key", base_url="https://different.example.com"
    )
    assert client1 is not client4

    client5 = llm.client("google", api_key=None, base_url=None)
    client6 = llm.client("google")
    assert client5 is client6
