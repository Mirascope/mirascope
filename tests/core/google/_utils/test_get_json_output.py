"""Tests the `google._utils.get_json_output` module."""

import pytest
from google.genai.types import (
    Candidate,
    Content,
    FunctionCall,
    GenerateContentResponse,
    Part,
)
from google.genai.types import (
    FinishReason as GoogleFinishReason,
)

from mirascope.core.google._utils._get_json_output import get_json_output
from mirascope.core.google.call_response import GoogleCallResponse
from mirascope.core.google.call_response_chunk import GoogleCallResponseChunk


@pytest.fixture()
def mock_generate_content_response() -> GenerateContentResponse:
    """Returns a mock `GenerateContentResponse` instance."""
    return GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[
                        Part(text='{"key": "value"}'),
                        Part(
                            function_call=FunctionCall(
                                name="FormatBook",
                                args={
                                    "title": "The Name of the Wind",
                                    "author": "Patrick Rothfuss",
                                },
                            )
                        ),
                    ],
                    role="model",
                ),
            )
        ]
    )


def test_get_json_output_call_response(
    mock_generate_content_response: GenerateContentResponse,
) -> None:
    """Tests the `get_json_output` function with a call response."""
    call_response = GoogleCallResponse(
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

    mock_generate_content_response.candidates[0].content.parts.pop(1)  # pyright: ignore [reportOptionalMemberAccess, reportOptionalSubscript]
    with pytest.raises(
        ValueError, match="No tool call or JSON object found in response."
    ):
        get_json_output(call_response, json_mode=False)


def test_get_json_output_call_response_chunk(
    mock_generate_content_response: GenerateContentResponse,
) -> None:
    """Tests the `get_json_output` function with a call response chunk."""
    call_response_chunk = GoogleCallResponseChunk(chunk=mock_generate_content_response)
    assert get_json_output(call_response_chunk, json_mode=True) == '{"key": "value"}'

    with pytest.raises(
        ValueError, match="Google only supports structured streaming in json mode."
    ):
        get_json_output(call_response_chunk, json_mode=False)
