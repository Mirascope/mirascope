"""Tests for base converter."""

from unittest.mock import patch

from mirascope.llm.clients.base import _extract_system_message
from mirascope.llm.messages import (
    assistant,
    system,
    user,
)


def test_encode_messages_with_system_first():
    """Test that system message is extracted when it's first."""
    messages = [
        system("You are a helpful assistant"),
        user("Hello"),
        assistant("Hi there"),
        user("How are you?"),
    ]

    system_message, rest = _extract_system_message(messages)

    assert system_message == "You are a helpful assistant"
    assert rest == messages[1:]


def test_encode_messages_no_system():
    """Test encoding messages when no system message is present."""
    messages = [
        user("Hello"),
        assistant("Hi there"),
        user("How are you?"),
    ]
    system_message, rest = _extract_system_message(messages)

    assert system_message is None
    assert rest == messages


def test_encode_messages_system_not_first_warns():
    """Test that system message not at index 0 is skipped with warning."""
    messages = [
        user("Hello"),
        system("You are a helpful assistant"),
        assistant("Hi there"),
    ]

    with patch("logging.warning") as mock_warning:
        system_message, rest = _extract_system_message(messages)

    assert system_message is None
    expected_rest = [messages[0], messages[2]]
    assert rest == expected_rest
    mock_warning.assert_called_once_with(
        "Skipping system message at index %d because it is not the first message",
        1,
    )


def test_encode_messages_multiple_system_warns():
    """Test that multiple system messages warn for non-first ones."""
    messages = [
        system("First system message"),
        user("Hello"),
        system("Second system message"),
        system("Third system message"),
    ]

    with patch("logging.warning") as mock_warning:
        system_message, rest = _extract_system_message(messages)

    assert system_message == "First system message"
    expected_rest = [messages[1]]
    assert rest == expected_rest
    assert mock_warning.call_count == 2
    mock_warning.assert_any_call(
        "Skipping system message at index %d because it is not the first message",
        2,
    )
    mock_warning.assert_any_call(
        "Skipping system message at index %d because it is not the first message",
        3,
    )


def test_encode_messages_empty_list():
    """Test encoding an empty message list."""
    messages = []

    system_message, rest = _extract_system_message(messages)

    assert system_message is None
    assert rest == []
