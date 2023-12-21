"""Tests for mirascope chat types."""
from mirascope.chat.types import MirascopeChatCompletion, MirascopeChatCompletionChunk


def test_mirascope_chat_completion(fixture_chat_completion):
    """Tests that `MirascopeChatCompletion` can be initialized properly."""
    mirascope_chat_completion = MirascopeChatCompletion(
        completion=fixture_chat_completion
    )
    choices = fixture_chat_completion.choices
    assert mirascope_chat_completion.choices == choices
    assert mirascope_chat_completion.choice == choices[0]
    assert mirascope_chat_completion.message == choices[0].message
    assert mirascope_chat_completion.content == choices[0].message.content
    assert str(mirascope_chat_completion) == mirascope_chat_completion.content


def test_mirascope_chat_completion_chunk(fixture_chat_completion_chunk):
    """Tests that `MirascopeChatCompletionStream` can be initialized properly."""
    mirascope_chat_completion_chunk = MirascopeChatCompletionChunk(
        chunk=fixture_chat_completion_chunk
    )
    choices = fixture_chat_completion_chunk.choices
    assert mirascope_chat_completion_chunk.choices == choices
    assert mirascope_chat_completion_chunk.delta == choices[0].delta
    assert mirascope_chat_completion_chunk.content == choices[0].delta.content
    assert (
        str(mirascope_chat_completion_chunk) == mirascope_chat_completion_chunk.content
    )
