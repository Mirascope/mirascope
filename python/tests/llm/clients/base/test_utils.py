"""Tests for base converter."""

from unittest.mock import patch

from mirascope.llm.clients.base import _utils
from mirascope.llm.messages import (
    assistant,
    system,
    user,
)


def test_encode_messages_with_system_first() -> None:
    """Test that system message is extracted when it's first."""
    messages = [
        system("You are a helpful assistant"),
        user("Hello"),
        assistant("Hi there"),
        user("How are you?"),
    ]

    system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message == "You are a helpful assistant"
    assert remaining_messages == messages[1:]


def test_encode_messages_no_system() -> None:
    """Test encoding messages when no system message is present."""
    messages = [
        user("Hello"),
        assistant("Hi there"),
        user("How are you?"),
    ]
    system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message is None
    assert remaining_messages == messages


def test_encode_messages_system_not_first_warns() -> None:
    """Test that system message not at index 0 is skipped with warning."""
    messages = [
        user("Hello"),
        system("You are a helpful assistant"),
        assistant("Hi there"),
    ]

    with patch("logging.warning") as mock_warning:
        system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message is None
    expected_remaining_messages = [messages[0], messages[2]]
    assert remaining_messages == expected_remaining_messages
    mock_warning.assert_called_once_with(
        "Skipping system message at index %d because it is not the first message",
        1,
    )


def test_encode_messages_multiple_system_warns() -> None:
    """Test that multiple system messages warn for non-first ones."""
    messages = [
        system("First system message"),
        user("Hello"),
        system("Second system message"),
        system("Third system message"),
    ]

    with patch("logging.warning") as mock_warning:
        system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message == "First system message"
    expected_remaining_messages = [messages[1]]
    assert remaining_messages == expected_remaining_messages
    assert mock_warning.call_count == 2
    mock_warning.assert_any_call(
        "Skipping system message at index %d because it is not the first message",
        2,
    )
    mock_warning.assert_any_call(
        "Skipping system message at index %d because it is not the first message",
        3,
    )


def test_encode_messages_empty_list() -> None:
    """Test encoding an empty message list."""
    messages = []

    system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message is None
    assert remaining_messages == []
