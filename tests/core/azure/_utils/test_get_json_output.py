"""Tests the `azure._utils.get_json_output` module."""

from datetime import datetime

import pytest
from azure.ai.inference.models import (
    ChatChoice,
    ChatCompletions,
    ChatCompletionsToolCall,
    ChatResponseMessage,
    CompletionsUsage,
    FunctionCall,
    StreamingChatChoiceUpdate,
    StreamingChatCompletionsUpdate,
    StreamingChatResponseMessageUpdate,
    StreamingChatResponseToolCallUpdate,
)

from mirascope.core.azure._utils._get_json_output import get_json_output
from mirascope.core.azure.call_response import AzureCallResponse
from mirascope.core.azure.call_response_chunk import AzureCallResponseChunk


def test_get_json_output_call_response() -> None:
    """Tests the `get_json_output` function with a call response."""
    tool_call = ChatCompletionsToolCall(
        id="id",
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
    )
    choices = [
        ChatChoice(
            finish_reason="stop",
            index=0,
            message=ChatResponseMessage(
                content="json_output", role="assistant", tool_calls=[tool_call]
            ),
        )
    ]
    completion = ChatCompletions(
        id="id",
        choices=choices,
        created=datetime.fromtimestamp(0),
        model="gpt-4o",
        usage=CompletionsUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2),
    )
    call_response = AzureCallResponse(
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

    completion.choices[0].message.content = ""
    completion.choices[0].message.tool_calls = []
    with pytest.raises(
        ValueError, match="No tool call or JSON object found in response."
    ):
        get_json_output(call_response, json_mode=False)


def test_get_json_output_call_response_chunk() -> None:
    """Tests the `get_json_output` function with a call response chunk."""
    tool_call = StreamingChatResponseToolCallUpdate(
        id="id",
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
    )
    choices = [
        StreamingChatChoiceUpdate(
            delta=StreamingChatResponseMessageUpdate(
                content="json_output", tool_calls=[tool_call]
            ),
            index=0,
            finish_reason="stop",
        )
    ]
    chunk = StreamingChatCompletionsUpdate(
        id="id",
        choices=choices,
        created=datetime.fromtimestamp(0),
        model="gpt-4o",
        usage=CompletionsUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2),
    )
    call_response_chunk = AzureCallResponseChunk(chunk=chunk)
    assert get_json_output(call_response_chunk, json_mode=True) == "json_output"
    assert (
        get_json_output(call_response_chunk, json_mode=False)
        == '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    )

    chunk.choices[0].delta.tool_calls = None
    assert get_json_output(call_response_chunk, json_mode=False) == ""
