"""Tests for OpenAICompletionsProvider"""

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.providers.openai.completions._utils import encode_request


def test_prepare_message_multiple_user_text_parts() -> None:
    """Test preparing an OpenAI request with multiple text parts in a user message.

    Included for code coverage.
    """

    messages = [
        llm.messages.user(["Hello there", "fellow humans"]),
    ]
    assert encode_request(
        model_id="openai/gpt-4o", messages=messages, format=None, tools=None, params={}
    ) == snapshot(
        (
            [
                llm.UserMessage(
                    content=[
                        llm.Text(text="Hello there"),
                        llm.Text(text="fellow humans"),
                    ]
                )
            ],
            None,
            {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": "Hello there", "type": "text"},
                            {"text": "fellow humans", "type": "text"},
                        ],
                    }
                ],
            },
        )
    )


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
    assert encode_request(
        model_id="openai/gpt-4o", messages=messages, format=None, tools=None, params={}
    ) == snapshot(
        (
            [
                llm.UserMessage(content=[llm.Text(text="Hello there")]),
                llm.AssistantMessage(
                    content=[llm.Text(text="General "), llm.Text(text="Kenobi")],
                    provider_id="openai",
                    model_id="openai/gpt-4o",
                    provider_model_name=None,
                    raw_message=None,
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
            model_id="openai/gpt-4",
            messages=messages,
            format=format,
            tools=None,
            params={},
        )
