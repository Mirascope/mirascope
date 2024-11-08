"""Tests the `cohere.stream` module."""

import pytest
from cohere.types import (
    ApiMeta,
    ApiMetaBilledUnits,
    ChatMessage,
    NonStreamedChatResponse,
    StreamEndStreamedChatResponse,
    StreamStartStreamedChatResponse,
    TextGenerationStreamedChatResponse,
)

from mirascope.core.cohere.call_response import CohereCallResponse
from mirascope.core.cohere.call_response_chunk import CohereCallResponseChunk
from mirascope.core.cohere.stream import CohereStream


def test_cohere_stream() -> None:
    """Tests the `CohereStream` class."""
    assert CohereStream._provider == "cohere"
    chunks = [
        StreamStartStreamedChatResponse(generation_id="id"),
        TextGenerationStreamedChatResponse(
            text="content",
        ),
        StreamEndStreamedChatResponse(
            finish_reason="COMPLETE",
            response=NonStreamedChatResponse(
                generation_id="id",
                text="content",
                meta=ApiMeta(
                    billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)
                ),
            ),
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = CohereCallResponseChunk(chunk=chunk)
            yield call_response_chunk, None

    stream = CohereStream(
        stream=generator(),
        metadata={},
        tool_types=None,
        call_response_type=CohereCallResponse,
        model="command-r-plus",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[ChatMessage(role="CHATBOT", message="content")],  # type: ignore
        call_params={},
        call_kwargs={},
    )

    with pytest.raises(
        ValueError, match="No stream response, check if the stream has been consumed."
    ):
        stream.construct_call_response()

    assert stream.cost is None
    for _ in stream:
        pass
    assert stream.cost == 1.8e-5
    assert stream.message_param == ChatMessage(
        role="assistant",  # type: ignore
        message="content",
        tool_calls=None,
    )


def test_construct_call_response() -> None:
    chunks = [
        StreamStartStreamedChatResponse(generation_id="id"),
        TextGenerationStreamedChatResponse(
            text="content",
        ),
        StreamEndStreamedChatResponse(
            finish_reason="COMPLETE",
            response=NonStreamedChatResponse(
                generation_id="id",
                text="content",
                meta=ApiMeta(
                    billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)
                ),
            ),
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = CohereCallResponseChunk(chunk=chunk)
            yield call_response_chunk, None

    stream = CohereStream(
        stream=generator(),
        metadata={},
        tool_types=None,
        call_response_type=CohereCallResponse,
        model="command-r-plus",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[ChatMessage(role="CHATBOT", message="content")],  # type: ignore
        call_params={},
        call_kwargs={},
    )
    assert stream.cost is None
    for _ in stream:
        pass
    constructed_call_response = stream.construct_call_response()
    usage = ApiMetaBilledUnits(input_tokens=1, output_tokens=1)
    completion = NonStreamedChatResponse(
        generation_id="id",
        text="content",
        finish_reason="COMPLETE",
        meta=ApiMeta(billed_units=usage),
    )
    call_response = CohereCallResponse(
        metadata={},
        response=completion,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    assert constructed_call_response.response == call_response.response


def test_construct_call_response_no_usage() -> None:
    """Tests the `GroqStream.construct_call_response` method with no usage."""
    chunks = [
        StreamStartStreamedChatResponse(generation_id="id"),
        TextGenerationStreamedChatResponse(
            text="content",
        ),
        StreamEndStreamedChatResponse(
            finish_reason="COMPLETE",
            response=NonStreamedChatResponse(
                generation_id="id", text="content", meta=None
            ),
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = CohereCallResponseChunk(chunk=chunk)
            yield call_response_chunk, None

    stream = CohereStream(
        stream=generator(),
        metadata={},
        tool_types=None,
        call_response_type=CohereCallResponse,
        model="command-r-plus",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[ChatMessage(role="CHATBOT", message="content")],  # type: ignore
        call_params={},
        call_kwargs={},
    )
    for _ in stream:
        pass
    constructed_call_response = stream.construct_call_response()
    assert constructed_call_response.usage is None
