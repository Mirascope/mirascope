"""Test for mirascope chat utility functions."""
import pytest

from mirascope.chat.utils import get_openai_chat_messages


@pytest.mark.parametrize(
    "prompt,expected_message_tuples",
    [
        (
            "fixture_foobar_prompt",
            "fixture_expected_foobar_prompt_messages",
        ),
        (
            "fixture_messages_prompt",
            "fixture_expected_messages_prompt_messages",
        ),
    ],
)
def test_get_openai_chat_messages(prompt, expected_message_tuples, request):
    """Tests that `get_openai_chat_messages` returns the expected messages."""
    prompt = request.getfixturevalue(prompt)
    expected_message_tuples = request.getfixturevalue(expected_message_tuples)
    messages = get_openai_chat_messages(prompt)
    assert len(messages) == len(expected_message_tuples)
    for message, expected_message_tuple in zip(messages, expected_message_tuples):
        assert message["role"] == expected_message_tuple[0]
        assert message["content"] == expected_message_tuple[1]
