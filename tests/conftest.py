"""Fixtures for repeated use in testing."""
import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk, ChoiceDelta
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice

from .test_prompts import FooBarPrompt, MessagesPrompt


@pytest.fixture()
def fixture_foobar_prompt():
    """Returns a `FooBarPrompt` instance."""
    return FooBarPrompt(foo="foo", bar="bar")


@pytest.fixture()
def fixture_expected_foobar_prompt_str():
    """Returns the expected string representation of `FooBarPrompt`."""
    return (
        "This is a test prompt about foobar. "
        "This should be on the same line in the template."
        "\n    This should be indented on a new line in the template."
    )


@pytest.fixture()
def fixture_expected_foobar_prompt_messages(fixture_expected_foobar_prompt_str):
    """Returns the expected messages parsed from `FooBarPrompt`."""
    return [("user", fixture_expected_foobar_prompt_str)]


@pytest.fixture()
def fixture_messages_prompt():
    """Returns a `MessagesPrompt` instance."""
    return MessagesPrompt(foo="foo", bar="bar")


@pytest.fixture()
def fixture_expected_messages_prompt_messages():
    """Returns the expected messages parsed from `MessagesPrompt`."""
    return [
        (
            "system",
            "This is the system message about foo.\n    "
            "This is also the system message.",
        ),
        ("user", "This is the user message about bar."),
        (
            "assistant",
            "This is an assistant message about foobar. "
            "This is also part of the assistant message.",
        ),
    ]


@pytest.fixture()
def fixture_chat_completion():
    """Returns a chat completion."""
    return ChatCompletion(
        id="test_id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="test content 0", role="assistant"
                ),
                **{"logprobs": None},
            ),
            Choice(
                finish_reason="stop",
                index=1,
                message=ChatCompletionMessage(
                    content="test content 1", role="assistant"
                ),
                **{"logprobs": None},
            ),
        ],
        created=0,
        model="test_model",
        object="chat.completion",
    )


@pytest.fixture()
def fixture_chat_completion_chunk():
    """Returns a chat completion chunk."""
    return ChatCompletionChunk(
        id="test_id",
        choices=[
            ChunkChoice(
                **{"logprobs": None},
                delta=ChoiceDelta(content="I'm"),
                finish_reason="stop",
                index=0,
            ),
            ChunkChoice(
                **{"logprobs": None},
                delta=ChoiceDelta(content="testing"),
                finish_reason="stop",
                index=0,
            ),
        ],
        created=0,
        model="test_model",
        object="chat.completion.chunk",
    )
