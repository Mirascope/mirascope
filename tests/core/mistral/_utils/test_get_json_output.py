"""Tests the `mistral._utils.get_json_output` module."""

import pytest
from mistralai.models import (
    AssistantMessage,
    ChatCompletionChoice,
    ChatCompletionResponse,
    CompletionChunk,
    CompletionResponseStreamChoice,
    DeltaMessage,
    FunctionCall,
    ToolCall,
    UsageInfo,
)

from mirascope.core.mistral._utils._get_json_output import get_json_output
from mirascope.core.mistral.call_response import MistralCallResponse
from mirascope.core.mistral.call_response_chunk import MistralCallResponseChunk


def test_get_json_output_call_response() -> None:
    """Tests the `get_json_output` function with a call response."""

    tool_call = ToolCall(
        id="id",
        function=FunctionCall(
            name="FormatBook",
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
        ),
        type="function",
    )
    choices = [
        ChatCompletionChoice(
            index=0,
            message=AssistantMessage(content="json_output", tool_calls=[tool_call]),
            finish_reason="stop",
        )
    ]
    completion = ChatCompletionResponse(
        id="id",
        object="",
        created=0,
        model="mistral-large-latest",
        choices=choices,
        usage=UsageInfo(prompt_tokens=1, completion_tokens=1, total_tokens=2),
    )
    call_response = MistralCallResponse(
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

    completion.choices[0].message.content = ""  # pyright: ignore [reportOptionalSubscript]
    completion.choices[0].message.tool_calls = None  # pyright: ignore [reportOptionalSubscript]
    with pytest.raises(
        ValueError, match="No tool call or JSON object found in response."
    ):
        get_json_output(call_response, json_mode=False)


def test_get_json_output_call_response_chunk() -> None:
    """Tests the `get_json_output` function with a call response chunk."""
    tool_call = ToolCall(
        id="id",
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="function",
        ),
        type="function",
    )
    choices = [
        CompletionResponseStreamChoice(
            index=0,
            delta=DeltaMessage(content="json_output", tool_calls=[tool_call]),
            finish_reason=None,
        )
    ]
    chunk = CompletionChunk(
        id="id",
        model="mistral-large-latest",
        choices=choices,
        created=0,
        object=None,
        usage=None,
    )
    call_response_chunk = MistralCallResponseChunk(chunk=chunk)
    assert get_json_output(call_response_chunk, json_mode=True) == "json_output"
    assert (
        get_json_output(call_response_chunk, json_mode=False)
        == '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    )

    chunk.choices[0].delta.tool_calls = None
    assert get_json_output(call_response_chunk, json_mode=False) == ""
