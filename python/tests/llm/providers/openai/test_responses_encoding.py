"""Tests for OpenAICompletionsProvider"""

from inline_snapshot import snapshot

from mirascope import llm
from mirascope.llm.providers.openai.responses._utils import encode_request


def test_prepare_message_multiple_assistant_text_parts() -> None:
    """Test preparing an OpenAI request with multiple text parts in an assistant message.

    Included for code coverage.
    """

    messages = [
        llm.messages.user("Hello there"),
        llm.messages.assistant(
            ["General ", "Kenobi"],
            model_id="openai/gpt-4o",
            provider_id="openai",
        ),
    ]
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=None,
        params={},
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
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=None,
        params={},
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
