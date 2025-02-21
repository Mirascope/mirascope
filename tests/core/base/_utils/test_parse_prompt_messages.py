"""Tests the `_utils.parse_prompt_messages` function."""

from unittest.mock import MagicMock, call, patch

import pytest

from mirascope.core.base import TextPart
from mirascope.core.base._utils._parse_prompt_messages import parse_prompt_messages


@patch(
    "mirascope.core.base._utils._parse_prompt_messages.parse_content_template",
    new_callable=MagicMock,
)
def test_parse_prompt_messages(mock_parse_content_template: MagicMock) -> None:
    """Test the parse_prompt_messages function."""
    empty_user_message = {"role": "user", "content": ""}
    mock_parse_content_template.return_value = empty_user_message

    messages = parse_prompt_messages(roles=["user"], template="prompt", attrs={})
    assert messages == [empty_user_message]
    mock_parse_content_template.assert_called_once_with("user", "prompt", {})
    mock_parse_content_template.reset_mock()

    prompt_template = """
    SYSTEM: 
    USER: This is a user message.
    """
    messages = parse_prompt_messages(
        roles=["system", "user"], template=prompt_template, attrs={}
    )
    assert messages == [empty_user_message, empty_user_message]
    mock_parse_content_template.assert_has_calls(
        [call("system", "", {}), call("user", "This is a user message.", {})]
    )

    prompt_template = """
    SYSTEM: This is a system message.
    MESSAGES: {messages}
    MESSAGES: {self.messages}
    USER: This is a user message.
    """
    mock_self = MagicMock()
    mock_messages = [empty_user_message, empty_user_message]
    mock_self.messages = mock_messages
    attrs = {"messages": mock_messages, "self": mock_self}
    messages = parse_prompt_messages(
        roles=["system", "user"], template=prompt_template, attrs=attrs
    )
    assert messages == [empty_user_message] * 6
    mock_parse_content_template.assert_has_calls(
        [
            call("system", "This is a system message.", attrs),
            call("user", "This is a user message.", attrs),
        ]
    )


def test_parse_prompt_messages_invalid_messages() -> None:
    """Test the parse_prompt_messages function with invalid messages."""
    with pytest.raises(ValueError):
        parse_prompt_messages(
            roles=["user"],
            template="MESSAGES: {self.messages}",
            attrs={},
        )

    with pytest.raises(ValueError):
        parse_prompt_messages(
            roles=["user"],
            template="MESSAGES: {messages}",
            attrs={"messages": "not a list"},
        )


def test_parse_prompt_messages_preserves_leading_newlines() -> None:
    """
    Test that parse_prompt_messages preserves leading newlines in the prompt text
    after splitting by roles.
    """
    template = """
    Caption this image: {text:text}
    Your caption should be concise.
    """
    messages = parse_prompt_messages(
        roles=["user"], template=template, attrs={"text": "foo"}
    )
    assert len(messages) == 1  # Only one user message
    assert messages[0].role == "user"
    assert messages[0].content == [
        TextPart(type="text", text="Caption this image:"),
        TextPart(type="text", text="foo"),
        TextPart(type="text", text="\nYour caption should be concise."),
    ]


def test_parse_prompt_messages_preserves_internal_newlines() -> None:
    """
    Test that parse_prompt_messages preserves internal newlines within a single role section.
    """
    template = """USER: First line
                Second line

                Third line
                """
    messages = parse_prompt_messages(roles=["user"], template=template, attrs={})
    assert len(messages) == 1
    user_message = messages[0]

    assert user_message.role == "user"

    expected_text = "First line\nSecond line\n\nThird line"
    assert user_message.content == expected_text, (
        f"Expected:\n{repr(expected_text)}\nGot:\n{repr(user_message.content)}"
    )
