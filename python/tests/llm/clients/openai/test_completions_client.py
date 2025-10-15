"""Tests for OpenAICompletionsClient"""

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.clients.openai.completions._utils import encode_request


def test_prepare_message_multiple_assistant_text_parts() -> None:
    """Test preparing an OpenAI request with multiple text parts in an assistant message.

    Included for code coverage.
    """

    messages = [
        llm.messages.user("Hello there"),
        llm.messages.assistant(
            ["General ", "Kenobi"], provider="openai:completions", model_id="gpt-4o"
        ),
    ]
    assert encode_request(
        model_id="gpt-4o", messages=messages, format=None, tools=None, params={}
    ) == snapshot(
        (
            [
                llm.UserMessage(content=[llm.Text(text="Hello there")]),
                llm.AssistantMessage(
                    content=[llm.Text(text="General "), llm.Text(text="Kenobi")],
                    provider="openai:completions",
                    model_id="gpt-4o",
                    raw_content=[],
                ),
            ],
            None,
            {
                "model": "gpt-4o",
                "messages": [
                    {"role": "user", "content": "Hello there"},
                    {
                        "role": "assistant",
                        "content": [
                            {"text": "General ", "type": "text"},
                            {"text": "Kenobi", "type": "text"},
                        ],
                    },
                ],
            },
        )
    )


def test_strict_unsupported_legacy_model() -> None:
    """Test the error thrown on a legacy model that doesn't support strict mode formatting.

    Included for code coverage.
    """

    messages = [llm.messages.user("I have a bad feeling about this...")]

    class Book(BaseModel):
        pass

    format = llm.format(Book, mode="strict")

    with pytest.raises(llm.FormattingModeNotSupportedError):
        encode_request(
            model_id="gpt-4", messages=messages, format=format, tools=None, params={}
        )


def test_context_manager() -> None:
    """Test nested context manager behavior and get_client() integration."""

    global_client = llm.get_client("openai:completions")

    client1 = llm.client("openai:completions", api_key="key1")
    client2 = llm.client("openai:completions", api_key="key2")

    assert llm.get_client("openai:completions") is global_client

    with client1 as ctx1:
        assert ctx1 is client1
        assert llm.get_client("openai:completions") is client1

        with client2 as ctx2:
            assert ctx2 is client2
            assert llm.get_client("openai:completions") is client2

        assert llm.get_client("openai:completions") is client1

    assert llm.get_client("openai:completions") is global_client


def test_client_caching() -> None:
    """Test that client() returns cached instances for identical parameters."""
    client1 = llm.client(
        "openai:completions", api_key="test-key", base_url="https://api.example.com"
    )
    client2 = llm.client(
        "openai:completions", api_key="test-key", base_url="https://api.example.com"
    )
    assert client1 is client2

    client3 = llm.client(
        "openai:completions",
        api_key="different-key",
        base_url="https://api.example.com",
    )
    assert client1 is not client3

    client4 = llm.client(
        "openai:completions",
        api_key="test-key",
        base_url="https://different.example.com",
    )
    assert client1 is not client4

    client5 = llm.client("openai:completions", api_key=None, base_url=None)
    client6 = llm.get_client("openai:completions")
    assert client5 is client6
