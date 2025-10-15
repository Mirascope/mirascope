"""Tests for OpenAICompletionsClient"""

from inline_snapshot import snapshot

from mirascope import llm
from mirascope.llm.clients.openai.responses._utils import encode_request


def test_prepare_message_multiple_assistant_text_parts() -> None:
    """Test preparing an OpenAI request with multiple text parts in an assistant message.

    Included for code coverage.
    """

    messages = [
        llm.messages.user("Hello there"),
        llm.messages.assistant(
            ["General ", "Kenobi"], provider="openai:responses", model_id="gpt-4o"
        ),
    ]
    _, _, kwargs = encode_request(
        model_id="gpt-4o", messages=messages, format=None, tools=None, params={}
    )
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {"role": "user", "content": "Hello there"},
                {"role": "assistant", "content": "General "},
                {"role": "assistant", "content": "Kenobi"},
            ],
        }
    )


def test_prepare_message_multiple_system_messages() -> None:
    """Test preparing an OpenAI request with multiple system messages."""

    messages = [
        llm.messages.user("Hello there"),
        llm.messages.system("Be concise."),
        llm.messages.system("On second thought, be verbose."),
    ]
    _, _, kwargs = encode_request(
        model_id="gpt-4o", messages=messages, format=None, tools=None, params={}
    )
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {"role": "user", "content": "Hello there"},
                {"role": "developer", "content": "Be concise."},
                {"role": "developer", "content": "On second thought, be verbose."},
            ],
        }
    )


def test_context_manager() -> None:
    """Test nested context manager behavior and get_client() integration."""

    global_client = llm.get_client("openai:responses")

    client1 = llm.client("openai:responses", api_key="key1")
    client2 = llm.client("openai:responses", api_key="key2")

    assert llm.get_client("openai:responses") is global_client

    with client1 as ctx1:
        assert ctx1 is client1
        assert llm.get_client("openai:responses") is client1

        with client2 as ctx2:
            assert ctx2 is client2
            assert llm.get_client("openai:responses") is client2

        assert llm.get_client("openai:responses") is client1

    assert llm.get_client("openai:responses") is global_client


def test_client_caching() -> None:
    """Test that client() returns cached instances for identical parameters."""
    client1 = llm.client(
        "openai:responses", api_key="test-key", base_url="https://api.example.com"
    )
    client2 = llm.client(
        "openai:responses", api_key="test-key", base_url="https://api.example.com"
    )
    assert client1 is client2

    client3 = llm.client(
        "openai:responses",
        api_key="different-key",
        base_url="https://api.example.com",
    )
    assert client1 is not client3

    client4 = llm.client(
        "openai:responses",
        api_key="test-key",
        base_url="https://different.example.com",
    )
    assert client1 is not client4

    client5 = llm.client("openai:responses", api_key=None, base_url=None)
    client6 = llm.get_client("openai:responses")
    assert client5 is client6
