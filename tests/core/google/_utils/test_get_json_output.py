"""Tests the `gemini._utils.get_json_output` module."""

import pytest
from google.ai.generativelanguage import (
    Candidate,
    Content,
    FunctionCall,
    GenerateContentResponse,
    Part,
)
from google.generativeai.types import (  # type: ignore
    GenerateContentResponse as GenerateContentResponseType,
)

from mirascope.core.gemini._utils._get_json_output import get_json_output
from mirascope.core.gemini.call_response import GeminiCallResponse
from mirascope.core.gemini.call_response_chunk import GeminiCallResponseChunk


@pytest.fixture()
def mock_generate_content_response() -> GenerateContentResponseType:
    """Returns a mock `GenerateContentResponse` instance."""
    return GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=1,
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
    )


def test_get_json_output_call_response(
    mock_generate_content_response: GenerateContentResponseType,
) -> None:
    """Tests the `get_json_output` function with a call response."""
    call_response = GeminiCallResponse(
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

    mock_generate_content_response.candidates[0].content.parts.pop(1)
    with pytest.raises(
        ValueError, match="No tool call or JSON object found in response."
    ):
        get_json_output(call_response, json_mode=False)


def test_get_json_output_call_response_chunk(
    mock_generate_content_response: GenerateContentResponseType,
) -> None:
    """Tests the `get_json_output` function with a call response chunk."""
    call_response_chunk = GeminiCallResponseChunk(chunk=mock_generate_content_response)
    assert get_json_output(call_response_chunk, json_mode=True) == '{"key": "value"}'

    with pytest.raises(
        ValueError, match="Gemini only supports structured streaming in json mode."
    ):
        get_json_output(call_response_chunk, json_mode=False)
