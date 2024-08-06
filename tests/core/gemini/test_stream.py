"""Tests the `gemini.stream` module."""

from google.ai.generativelanguage import (
    Candidate,
    Content,
    GenerateContentResponse,
    Part,
)
from google.generativeai.types import (  # type: ignore
    GenerateContentResponse as GenerateContentResponseType,
)

from mirascope.core.gemini.call_response import GeminiCallResponse
from mirascope.core.gemini.call_response_chunk import GeminiCallResponseChunk
from mirascope.core.gemini.stream import GeminiStream


def test_gemini_stream() -> None:
    """Tests the `GeminiStream` class."""
    assert GeminiStream._provider == "gemini"

    chunks = [
        GenerateContentResponseType.from_response(
            GenerateContentResponse(
                candidates=[
                    Candidate(
                        finish_reason=1,
                        content=Content(
                            parts=[Part(text="The author is ")], role="model"
                        ),
                    )
                ]
            )
        ),
        GenerateContentResponseType.from_response(
            GenerateContentResponse(
                candidates=[
                    Candidate(
                        finish_reason=1,
                        content=Content(
                            parts=[Part(text="Patrick Rothfuss")], role="model"
                        ),
                    )
                ]
            )
        ),
    ]
    stream = GeminiStream(
        stream=((GeminiCallResponseChunk(chunk=chunk), None) for chunk in chunks),
        metadata={},
        tool_types=None,
        call_response_type=GeminiCallResponse,
        model="gemini-flash-1.5",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "parts": ["Who is the author?"]}],
        call_params={},
        call_kwargs={},
    )
    assert stream.cost is None
    for _ in stream:
        pass
    assert stream.cost is None
    assert stream.message_param == {
        "role": "model",
        "parts": [{"text": "The author is Patrick Rothfuss"}],
    }


def test_construct_call_response():
    chunks = [
        GenerateContentResponseType.from_response(
            GenerateContentResponse(
                candidates=[
                    Candidate(
                        finish_reason=1,
                        content=Content(
                            parts=[Part(text="The author is ")], role="model"
                        ),
                    )
                ]
            )
        ),
        GenerateContentResponseType.from_response(
            GenerateContentResponse(
                candidates=[
                    Candidate(
                        finish_reason=1,
                        content=Content(
                            parts=[Part(text="Patrick Rothfuss")], role="model"
                        ),
                    )
                ]
            )
        ),
    ]
    stream = GeminiStream(
        stream=((GeminiCallResponseChunk(chunk=chunk), None) for chunk in chunks),
        metadata={},
        tool_types=None,
        call_response_type=GeminiCallResponse,
        model="gemini-flash-1.5",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "parts": ["Who is the author?"]}],
        call_params={},
        call_kwargs={},
    )

    for _ in stream:
        pass

    response = GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=1,
                    content=Content(
                        parts=[Part(text="The author is Patrick Rothfuss")],
                        role="model",
                    ),
                )
            ]
        )
    )
    call_response = GeminiCallResponse(
        metadata={},
        response=response,
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
    assert constructed_call_response._provider == call_response._provider
    assert constructed_call_response.content == call_response.content
    assert constructed_call_response.finish_reasons == call_response.finish_reasons
    assert constructed_call_response.model == call_response.model
    assert constructed_call_response.id == call_response.id
    assert constructed_call_response.usage == call_response.usage
    assert constructed_call_response.input_tokens == call_response.input_tokens
    assert constructed_call_response.output_tokens == call_response.output_tokens
    assert constructed_call_response.cost == call_response.cost
    assert constructed_call_response.message_param == call_response.message_param
