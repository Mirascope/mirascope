"""Tests the `_utils.get_possible_user_message_param` module."""

from pydantic import BaseModel

from mirascope.core.base._utils._get_possible_user_message_param import (
    get_possible_user_message_param,
)


def test_get_possible_user_message_param() -> None:
    """Tests the `get_possible_user_message_param` function."""
    assert get_possible_user_message_param([]) is None

    messages = [{"role": "user", "text": "Hello, world!"}]
    assert get_possible_user_message_param(messages) == messages[0]

    messages = [{"role": "assistant", "text": "Hi!"}]
    assert get_possible_user_message_param(messages) is None

    messages = [
        {"role": "user", "text": "Hello, world!"},
        {"role": "assistant", "text": "Hi!"},
    ]
    assert get_possible_user_message_param(messages) is None

    messages = [
        {"role": "user", "text": "Hello!"},
        {"role": "assistant", "text": "Hi!"},
        {"role": "user", "text": "How are you?"},
    ]
    assert get_possible_user_message_param(messages) == messages[-1]

    class Message(BaseModel):
        role: str
        text: str

    messages = [Message(role="user", text="Hello, world!")]
    assert get_possible_user_message_param(messages) == messages[0]

    messages = [Message(role="assistant", text="Hi!")]
    assert get_possible_user_message_param(messages) is None

    messages = [
        Message(role="user", text="Hello, world!"),
        Message(role="assistant", text="Hi!"),
    ]
    assert get_possible_user_message_param(messages) is None

    messages = [
        Message(role="user", text="Hello!"),
        Message(role="assistant", text="Hi!"),
        Message(role="user", text="How are you?"),
    ]
    assert get_possible_user_message_param(messages) == messages[-1]
