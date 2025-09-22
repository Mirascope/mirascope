"""Tests for OpenAIClient"""

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.clients.openai import _utils as openai_utils


def test_prepare_message_multiple_assistant_text_parts() -> None:
    """Test preparing an OpenAI request with multiple text parts in an assistant message.

    Included for code coverage.
    """

    messages = [
        llm.messages.user("Hello there"),
        llm.messages.assistant(["General ", "Kenobi"]),
    ]
    assert openai_utils.prepare_openai_request(
        model_id="gpt-4o", messages=messages
    ) == snapshot(
        (
            [
                llm.UserMessage(content=[llm.Text(text="Hello there")]),
                llm.AssistantMessage(
                    content=[llm.Text(text="General "), llm.Text(text="Kenobi")]
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
        openai_utils.prepare_openai_request(
            model_id="gpt-4", messages=messages, format=format
        )
