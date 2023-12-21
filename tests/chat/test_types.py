"""Tests for Mirascope chat types."""
import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk, ChoiceDelta
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice

from mirascope.chat.types import MirascopeChatCompletion, MirascopeChatCompletionChunk


@pytest.mark.parametrize(
    "choices",
    [
        [
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(content="test content", role="assistant"),
                **{"logprobs": None},
            )
        ],
        [
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
    ],
)
def test_mirascope_chat_completion(choices: list[Choice]):
    """Tests that `MirascopeChatCompletion` can be initialized properly."""
    chat_completion = ChatCompletion(
        id="test_id",
        choices=choices,
        created=0,
        model="test_model",
        object="chat.completion",
    )
    mirascope_chat_completion = MirascopeChatCompletion(completion=chat_completion)
    assert mirascope_chat_completion.choices == choices
    assert mirascope_chat_completion.choice == choices[0]
    assert mirascope_chat_completion.message == choices[0].message
    assert mirascope_chat_completion.content == choices[0].message.content
    assert str(mirascope_chat_completion) == mirascope_chat_completion.content


@pytest.mark.parametrize(
    "choices",
    [
        [
            ChunkChoice(
                **{"logprobs": None},
                delta=ChoiceDelta(content="I'm"),
                finish_reason="stop",
                index=0,
            )
        ],
        [
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
    ],
)
def test_mirascope_chat_completion_chunk(choices: list[ChunkChoice]):
    """Tests that `MirascopeChatCompletionStream` can be initialized properly."""
    chat_completion_chunk = ChatCompletionChunk(
        id="test_id",
        choices=choices,
        created=0,
        model="test_model",
        object="chat.completion.chunk",
    )
    mirascope_chat_completion_chunk = MirascopeChatCompletionChunk(
        chunk=chat_completion_chunk
    )
    assert mirascope_chat_completion_chunk.choices == choices
    assert mirascope_chat_completion_chunk.delta == choices[0].delta
    assert mirascope_chat_completion_chunk.content == choices[0].delta.content
    assert (
        str(mirascope_chat_completion_chunk) == mirascope_chat_completion_chunk.content
    )
