"""Tests the `vertex._utils.get_json_output` module."""

import pytest
from google.cloud.aiplatform_v1beta1.types import FunctionCall
from vertexai.generative_models import (
    Candidate,
    Content,
    Part,
)
from vertexai.generative_models import (
    GenerationResponse as GenerateContentResponse,
)

from mirascope.core.vertex._utils._get_json_output import get_json_output
from mirascope.core.vertex.call_response import VertexCallResponse
from mirascope.core.vertex.call_response_chunk import VertexCallResponseChunk


@pytest.fixture()
def mock_generate_content_response() -> GenerateContentResponse:
    """Returns a mock `GenerateContentResponse` instance."""
    raw_part = Part()
    raw_part._raw_part.function_call = FunctionCall(
        name="FormatBook",
        args={
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
        },
    )
    return GenerateContentResponse.from_dict(
        {
            "candidates": [
                Candidate.from_dict(
                    {
                        "finish_reason": 1,
                        "content": Content(
                            parts=[
                                Part.from_text('{"key": "value"}'),
                                raw_part,
                            ],
                            role="model",
                        ).to_dict(),
                    }
                ).to_dict()
            ]
        }
    )


def test_get_json_output_call_response(
    mock_generate_content_response: GenerateContentResponse,
) -> None:
    """Tests the `get_json_output` function with a call response."""
    call_response = VertexCallResponse(
        metadata={},
        response=mock_generate_content_response,
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
    assert get_json_output(call_response, json_mode=True) == '{"key": "value"}'
    assert (
        get_json_output(call_response, json_mode=False)
        == '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    )

    mock_generate_content_response._raw_response.candidates[0].content.parts.pop(1)
    with pytest.raises(
        ValueError, match="No tool call or JSON object found in response."
    ):
        get_json_output(call_response, json_mode=False)


def test_get_json_output_call_response_chunk(
    mock_generate_content_response: GenerateContentResponse,
) -> None:
    """Tests the `get_json_output` function with a call response chunk."""
    call_response_chunk = VertexCallResponseChunk(chunk=mock_generate_content_response)
    assert get_json_output(call_response_chunk, json_mode=True) == '{"key": "value"}'

    with pytest.raises(
        ValueError, match="Vertex only supports structured streaming in json mode."
    ):
        get_json_output(call_response_chunk, json_mode=False)
