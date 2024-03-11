"""Tests for the `BasePrompt` class."""
from typing import Any

import pytest
from pydantic import ConfigDict

from mirascope.base.prompts import BasePrompt
from mirascope.base.types import Message


@pytest.mark.parametrize(
    "prompt_tags,prompt_template,prompt_data,expected_str,expected_messages,"
    "expected_dump",
    [
        (
            ["version:0001"],
            "Single user message",
            {},
            "Single user message",
            [{"role": "user", "content": "Single user message"}],
            {
                "tags": ["version:0001"],
                "template": "Single user message",
                "inputs": {},
            },
        ),
        (
            ["multiple", "different", "tags"],
            """\
                SYSTEM: system message
                USER: user message about {topic}
            """,
            {"topic": "testing"},
            "SYSTEM: system message\nUSER: user message about testing",
            [
                {"role": "system", "content": "system message"},
                {"role": "user", "content": "user message about testing"},
            ],
            {
                "tags": ["multiple", "different", "tags"],
                "template": "SYSTEM: system message\nUSER: user message about {topic}",
                "inputs": {"topic": "testing"},
            },
        ),
    ],
)
def test_base_prompt(
    prompt_tags: list[str],
    prompt_template: str,
    prompt_data: dict[str, Any],
    expected_str: str,
    expected_messages: list[Message],
    expected_dump: dict[str, Any],
) -> None:
    """Tests various different subclasses of `BasePrompt`."""

    class Prompt(BasePrompt):
        tags = prompt_tags
        template = prompt_template

        model_config = ConfigDict(extra="allow")

    prompt = Prompt(**prompt_data)
    assert str(prompt) == expected_str
    assert prompt.messages() == expected_messages
    assert prompt.dump() == expected_dump


def test_base_prompt_bad_message_role() -> None:
    """Tests that a bad message role throws an error."""
    with pytest.raises(ValueError):

        class Prompt(BasePrompt):
            template = "BAD: Bad role should throw error"

        Prompt().messages()
