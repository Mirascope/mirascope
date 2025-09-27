"""Tests for llm.clients.GoogleClient."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from mirascope import llm
from mirascope.llm.clients.google._utils import prepare_google_request


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


def test_context_manager() -> None:
    """Test nested context manager behavior and get_client() integration."""

    global_client = llm.get_client("google")

    client1 = llm.client("google", api_key="key1")
    client2 = llm.client("google", api_key="key2")

    assert llm.get_client("google") is global_client

    with client1 as ctx1:
        assert ctx1 is client1
        assert llm.get_client("google") is client1

        with client2 as ctx2:
            assert ctx2 is client2
            assert llm.get_client("google") is client2

        assert llm.get_client("google") is client1

    assert llm.get_client("google") is global_client


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
    client6 = llm.get_client("google")
    assert client5 is client6


def test_prepare_google_request_frequency_penalty_logging(
    caplog: pytest.LogCaptureFixture,
) -> None:
    messages = [llm.messages.user("test message")]

    with caplog.at_level(logging.WARNING):
        _, _, _, config = prepare_google_request(
            model_id="gemini-2.5-pro",
            messages=messages,
            params={"frequency_penalty": 0.5},
        )

    assert len(caplog.records) == 1
    assert (
        "parameter frequency_penalty is not supported for model gemini-2.5-pro - ignoring"
        in caplog.records[0].message
    )
    assert config is None or not hasattr(config, "frequency_penalty")

    caplog.clear()

    with caplog.at_level(logging.WARNING):
        _, _, _, config = prepare_google_request(
            model_id="gemini-2.0-flash",
            messages=messages,
            params={"frequency_penalty": 0.5},
        )

    assert len(caplog.records) == 0
    assert config is not None
    assert config.get("frequency_penalty") == 0.5


def test_prepare_google_request_presence_penalty_logging(
    caplog: pytest.LogCaptureFixture,
) -> None:
    messages = [llm.messages.user("test message")]

    with caplog.at_level(logging.WARNING):
        _, _, _, config = prepare_google_request(
            model_id="gemini-2.5-flash",
            messages=messages,
            params={"presence_penalty": 0.3},
        )

    assert len(caplog.records) == 1
    assert (
        "parameter presence_penalty is not supported for model gemini-2.5-flash - ignoring"
        in caplog.records[0].message
    )
    assert config is not None or not hasattr(config, "presence_penalty")

    caplog.clear()

    with caplog.at_level(logging.WARNING):
        _, _, _, config = prepare_google_request(
            model_id="gemini-2.0-flash",
            messages=messages,
            params={"presence_penalty": 0.3},
        )

    assert len(caplog.records) == 0
    assert config is not None
    assert config.get("presence_penalty") == 0.3
