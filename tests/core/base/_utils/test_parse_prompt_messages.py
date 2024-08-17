"""Tests the `_utils.parse_prompt_messages` function."""

from unittest.mock import MagicMock, call, patch

import pytest

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
