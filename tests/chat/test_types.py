"""Tests for mirascope chat types."""
from mirascope.chat.types import OpenAIChatCompletion, OpenAIChatCompletionChunk


def test_openai_chat_completion(fixture_chat_completion):
    """Tests that `OpenAIChatCompletion` can be initialized properly."""
    openai_chat_completion = OpenAIChatCompletion(completion=fixture_chat_completion)
    choices = fixture_chat_completion.choices
    assert openai_chat_completion.choices == choices
    assert openai_chat_completion.choice == choices[0]
    assert openai_chat_completion.message == choices[0].message
    assert openai_chat_completion.content == choices[0].message.content
    assert str(openai_chat_completion) == openai_chat_completion.content


def test_openai_chat_completion_chunk(fixture_chat_completion_chunk):
    """Tests that `OpenAIChatCompletionChunk` can be initialized properly."""
    openai_chat_completion_chunk = OpenAIChatCompletionChunk(
        chunk=fixture_chat_completion_chunk
    )
    choices = fixture_chat_completion_chunk.choices
    assert openai_chat_completion_chunk.choices == choices
    assert openai_chat_completion_chunk.delta == choices[0].delta
    assert openai_chat_completion_chunk.content == choices[0].delta.content
    assert str(openai_chat_completion_chunk) == openai_chat_completion_chunk.content
