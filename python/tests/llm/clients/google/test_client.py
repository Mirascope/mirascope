"""Tests for llm.clients.GoogleClient."""

from unittest.mock import MagicMock, patch

from mirascope import llm


def test_custom_base_url() -> None:
    """Test that custom base URL is used for API requests."""
    example_url = "https://example.com"

    with patch("mirascope.llm.clients.google.client.Client") as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        google_client = llm.GoogleClient(base_url=example_url)

        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        assert call_args.kwargs["http_options"] is not None
        assert call_args.kwargs["http_options"].base_url == example_url

        assert google_client.client is mock_client_instance


def test_context_manager() -> None:
    """Test nested context manager behavior and get_client() integration."""

    global_client = llm.get_client("google")

    client1 = llm.GoogleClient(api_key="key1")
    client2 = llm.GoogleClient(api_key="key2")

    assert llm.get_client("google") is global_client

    with client1 as ctx1:
        assert ctx1 is client1
        assert llm.get_client("google") is client1

        with client2 as ctx2:
            assert ctx2 is client2
            assert llm.get_client("google") is client2

        assert llm.get_client("google") is client1

    assert llm.get_client("google") is global_client
