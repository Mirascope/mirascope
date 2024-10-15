"""Tests the `cohere._utils.get_json_output` module."""

import pytest
from cohere.types import (
    NonStreamedChatResponse,
    StreamEndStreamedChatResponse,
    TextGenerationStreamedChatResponse,
    ToolCall,
    ToolCallsGenerationStreamedChatResponse,
)

from mirascope.core.cohere._utils._get_json_output import get_json_output
from mirascope.core.cohere.call_response import CohereCallResponse
from mirascope.core.cohere.call_response_chunk import CohereCallResponseChunk


def test_get_json_output_call_response() -> None:
    """Tests the `get_json_output` function with a call response."""
    tool_call = ToolCall(
        name="FormatBook",
        parameters={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
    )
    completion = NonStreamedChatResponse(
        generation_id="id",
        text="json_output",
        finish_reason="COMPLETE",
        meta=None,
        tool_calls=[tool_call],
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
    assert get_json_output(call_response, json_mode=True) == "json_output"
    assert (
        get_json_output(call_response, json_mode=False)
        == '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    )

    call_response = CohereCallResponse(
        metadata={},
        response=NonStreamedChatResponse(
            generation_id="id",
            text="",
            finish_reason="COMPLETE",
            meta=None,
        ),
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
    with pytest.raises(
        ValueError, match="No tool call or JSON object found in response."
    ):
        get_json_output(call_response, json_mode=False)


def test_get_json_output_call_response_chunk() -> None:
    """Tests the `get_json_output` function with a call response chunk."""
    chunk_text_generation = TextGenerationStreamedChatResponse(
        text="json_output",
    )
    call_response_chunk_text_generation = CohereCallResponseChunk(
        chunk=chunk_text_generation
    )
    assert (
        get_json_output(call_response_chunk_text_generation, json_mode=True)
        == "json_output"
    )
    tool_call = ToolCall(
        name="FormatBook",
        parameters={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
    )
    chunk_tool_calls = ToolCallsGenerationStreamedChatResponse(tool_calls=[tool_call])
    call_response_chunk_tool_calls = CohereCallResponseChunk(chunk=chunk_tool_calls)
    assert (
        get_json_output(call_response_chunk_tool_calls, json_mode=False)
        == '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    )
    chunk_end = StreamEndStreamedChatResponse(
        finish_reason="COMPLETE",
        response=NonStreamedChatResponse(generation_id="id", text="", meta=None),
    )
    call_response_chunk_end = CohereCallResponseChunk(chunk=chunk_end)
    assert get_json_output(call_response_chunk_end, json_mode=False) == ""
