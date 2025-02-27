"""Tests the `litellm.stream` module."""

from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta
from openai.types.completion_usage import CompletionUsage

from mirascope.core.base.types import CostMetadata
from mirascope.core.litellm.call_response import LiteLLMCallResponse
from mirascope.core.litellm.call_response_chunk import LiteLLMCallResponseChunk
from mirascope.core.litellm.stream import LiteLLMStream


def test_litellm_stream_cost() -> None:
    """Tests the `LiteLLMStream` cost property."""
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
            model="claude-3-5-sonnet-20240620",
            object="chat.completion.chunk",
            usage=usage,
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = LiteLLMCallResponseChunk(chunk=chunk)
            yield call_response_chunk, None

    stream = LiteLLMStream(
        stream=generator(),
        metadata={},
        tool_types=None,
        call_response_type=LiteLLMCallResponse,
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

    assert stream.cost == 3.9e-05
    assert stream.cost_metadata == CostMetadata(cost=3.9e-05)
    assert stream.model == "claude-3-5-sonnet-20240620"
