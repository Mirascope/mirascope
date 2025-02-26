"""Tests the `google.stream` module."""

import pytest
from google.genai.types import (
    Candidate,
    Content,
    ContentDict,
    GenerateContentResponse,
    GenerateContentResponseUsageMetadata,
    Part,
    PartDict,
)
from google.genai.types import (
    FinishReason as GoogleFinishReason,
)

from mirascope.core.base.types import CostMetadata
from mirascope.core.google.call_response import GoogleCallResponse
from mirascope.core.google.call_response_chunk import GoogleCallResponseChunk
from mirascope.core.google.stream import GoogleStream


def test_google_stream() -> None:
    """Tests the `GoogleStream` class."""
    assert GoogleStream._provider == "google"

    chunks = [
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=GoogleFinishReason.STOP,
                    content=Content(parts=[Part(text="The author is ")], role="model"),
                )
            ]
        ),
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=GoogleFinishReason.STOP,
                    content=Content(
                        parts=[Part(text="Patrick Rothfuss")], role="model"
                    ),
                )
            ]
        ),
    ]
    stream = GoogleStream(
        stream=((GoogleCallResponseChunk(chunk=chunk), None) for chunk in chunks),
        metadata={},
        tool_types=None,
        call_response_type=GoogleCallResponse,
        model="google-1.5-flash",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "parts": [{"text": "Who is the author?"}]}],
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
    assert stream.cost is None
    assert stream.cost_metadata == CostMetadata()
    assert stream.message_param == {
        "role": "model",
        "parts": [{"text": "The author is Patrick Rothfuss"}],
    }


def test_construct_call_response() -> None:
    chunks = [
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=GoogleFinishReason.STOP,
                    content=Content(parts=[Part(text="The author is ")], role="model"),
                )
            ]
        ),
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=GoogleFinishReason.STOP,
                    content=Content(
                        parts=[Part(text="Patrick Rothfuss")], role="model"
                    ),
                )
            ]
        ),
    ]
    stream = GoogleStream(
        stream=((GoogleCallResponseChunk(chunk=chunk), None) for chunk in chunks),
        metadata={},
        tool_types=None,
        call_response_type=GoogleCallResponse,
        model="google-1.5-flash",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[
            ContentDict(role="user", parts=[PartDict(text="Who is the author?")])
        ],
        call_params={},
        call_kwargs={},
    )

    for _ in stream:
        pass

    response = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[Part(text="The author is Patrick Rothfuss")],
                    role="model",
                ),
            )
        ],
        model_version="google-1.5-flash",
        usage_metadata=GenerateContentResponseUsageMetadata(
            candidates_token_count=None, prompt_token_count=None, total_token_count=0
        ),
    )
    call_response = GoogleCallResponse(
        metadata={},
        response=response,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param={},
        start_time=0,
        end_time=0,
    )
    constructed_call_response = stream.construct_call_response()
    assert constructed_call_response.response.__eq__(call_response.response)
