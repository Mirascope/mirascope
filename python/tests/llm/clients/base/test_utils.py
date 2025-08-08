"""Tests for base converter."""

from unittest.mock import patch

from mirascope import llm
from mirascope.llm.clients.base import _utils


def test_encode_messages_with_system_first() -> None:
    """Test that system message is extracted when it's first."""
    messages = [
        llm.messages.system("You are a helpful assistant"),
        llm.messages.user("Hello"),
        llm.messages.assistant("Hi there"),
        llm.messages.user("How are you?"),
    ]

    system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message == "You are a helpful assistant"
    assert remaining_messages == messages[1:]


def test_encode_messages_no_system() -> None:
    """Test encoding messages when no system message is present."""
    messages = [
        llm.messages.user("Hello"),
        llm.messages.assistant("Hi there"),
        llm.messages.user("How are you?"),
    ]
    system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message is None
    assert remaining_messages == messages


def test_encode_messages_system_not_first_warns() -> None:
    """Test that system message not at index 0 is skipped with warning."""
    messages = [
        llm.messages.user("Hello"),
        llm.messages.system("You are a helpful assistant"),
        llm.messages.assistant("Hi there"),
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
        llm.messages.system("First system message"),
        llm.messages.user("Hello"),
        llm.messages.system("Second system message"),
        llm.messages.system("Third system message"),
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
