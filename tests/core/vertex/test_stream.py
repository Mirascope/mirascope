"""Tests the `vertex.stream` module."""

import pytest
from vertexai.generative_models import (
    Candidate,
    Content,
    FinishReason,
    Part,
)
from vertexai.generative_models import (
    GenerationResponse as GenerateContentResponse,
)

from mirascope.core.base.types import CostMetadata
from mirascope.core.vertex.call_response import VertexCallResponse
from mirascope.core.vertex.call_response_chunk import VertexCallResponseChunk
from mirascope.core.vertex.stream import VertexStream


def test_vertex_stream() -> None:
    """Tests the `VertexStream` class."""
    assert VertexStream._provider == "vertex"

    chunks = [
        GenerateContentResponse.from_dict(
            {
                "candidates": [
                    Candidate.from_dict(
                        {
                            "finish_reason": 1,
                            "content": Content(
                                parts=[Part.from_text("The author is ")],
                                role="model",
                            ).to_dict(),
                        },
                    ).to_dict()
                ]
            }
        ),
        GenerateContentResponse.from_dict(
            {
                "candidates": [
                    Candidate.from_dict(
                        {
                            "finish_reason": 1,
                            "content": Content(
                                parts=[Part.from_text("Patrick Rothfuss")], role="model"
                            ).to_dict(),
                        }
                    ).to_dict()
                ]
            }
        ),
    ]
    stream = VertexStream(
        stream=((VertexCallResponseChunk(chunk=chunk), None) for chunk in chunks),
        metadata={},
        tool_types=None,
        call_response_type=VertexCallResponse,
        model="gemini-1.5-flash",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[Content(role="user", parts=[Part.from_text("Who is the author?")])],
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
    assert stream.message_param.role == "model"
    assert len(stream.message_param.parts) == 1
    assert stream.message_param.parts[0].text == "The author is Patrick Rothfuss"
    assert stream.cost_metadata == CostMetadata()


def test_construct_call_response() -> None:
    chunks = [
        GenerateContentResponse.from_dict(
            {
                "candidates": [
                    Candidate.from_dict(
                        {
                            "content": Content(
                                parts=[Part.from_text("The author is ")], role="model"
                            ).to_dict(),
                            "finish_reason": FinishReason.STOP,
                        }
                    ).to_dict()
                ]
            }
        ),
        GenerateContentResponse.from_dict(
            {
                "candidates": [
                    Candidate.from_dict(
                        {
                            "content": Content(
                                parts=[Part.from_text("Patrick Rothfuss")], role="model"
                            ).to_dict(),
                            "finish_reason": FinishReason.STOP,
                        }
                    ).to_dict()
                ]
            }
        ),
    ]
    stream = VertexStream(
        stream=((VertexCallResponseChunk(chunk=chunk), None) for chunk in chunks),
        metadata={},
        tool_types=None,
        call_response_type=VertexCallResponse,
        model="gemini-1.5-flash",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[Content(role="user", parts=[Part.from_text("Who is the author?")])],
        call_params={},
        call_kwargs={},
    )

    for _ in stream:
        pass

    expected_response = GenerateContentResponse.from_dict(
        {
            "candidates": [
                Candidate.from_dict(
                    {
                        "content": Content(
                            parts=[Part.from_text("The author is Patrick Rothfuss")],
                            role="model",
                        ).to_dict(),
                        "finish_reason": FinishReason.STOP,
                    }
                ).to_dict()
            ]
        }
    )
    call_response = VertexCallResponse(
        metadata={},
        response=expected_response,
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
    constructed_call_response = stream.construct_call_response()
    assert (
        constructed_call_response.response.to_dict() == call_response.response.to_dict()
    )
