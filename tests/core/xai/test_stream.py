"""Tests the `xai.stream` module."""

from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta
from openai.types.completion_usage import CompletionUsage

from mirascope.core.xai.call_response import XAICallResponse
from mirascope.core.xai.call_response_chunk import XAICallResponseChunk
from mirascope.core.xai.stream import XAIStream


def test_xai_stream_cost() -> None:
    """Tests the `XAIStream` cost property."""
    usage = CompletionUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2)
    chunks = [
        ChatCompletionChunk(
            id="id",
            choices=[
                ChunkChoice(
                    delta=ChoiceDelta(content="content", tool_calls=None), index=0
                )
            ],
            created=0,
            model="grok-3",
            object="chat.completion.chunk",
            usage=usage,
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = XAICallResponseChunk(chunk=chunk)
            yield call_response_chunk, None

    stream = XAIStream(
        stream=generator(),
        metadata={},
        tool_types=None,
        call_response_type=XAICallResponse,
        model="",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "content": "content"}],
        call_params={},
        call_kwargs={},
    )

    for _ in stream:
        pass

    assert stream.cost == 1.4e-5
    assert stream.model == "grok-3"
