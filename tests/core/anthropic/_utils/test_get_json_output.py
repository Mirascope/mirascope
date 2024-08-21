"""Tests the `anthropic._utils.get_json_output` module."""

import pytest
from anthropic.types import (
    Message,
    RawContentBlockDeltaEvent,
    TextBlock,
    TextDelta,
    ToolUseBlock,
    Usage,
)

try:
    from anthropic.types import (
        InputJsonDelta as InputJSONDelta,  # pyright: ignore [reportAttributeAccessIssue]
    )
except ImportError:
    from anthropic.types import (
        InputJSONDelta,  # pyright: ignore [reportAttributeAccessIssue]
    )

from mirascope.core.anthropic._utils._get_json_output import get_json_output
from mirascope.core.anthropic.call_params import AnthropicCallParams
from mirascope.core.anthropic.call_response import AnthropicCallResponse
from mirascope.core.anthropic.call_response_chunk import AnthropicCallResponseChunk


def test_get_json_output_call_response() -> None:
    """Tests the `get_json_output` function with a call response."""
    usage = Usage(input_tokens=1, output_tokens=1)
    text = TextBlock(
        type="text",
        text='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
    )
    completion = Message(
        id="id",
        content=[text],
        model="claude-3-5-sonnet-20240620",
        role="assistant",
        stop_reason="end_turn",
        stop_sequence=None,
        type="message",
        usage=usage,
    )
    call_response = AnthropicCallResponse(
        metadata={},
        response=completion,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=AnthropicCallParams(max_tokens=1000),
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    assert (
        get_json_output(call_response, json_mode=True)
        == '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    )
    completion.content[0] = ToolUseBlock(
        type="tool_use",
        id="id",
        input={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
        name="FormatBook",
    )

    assert (
        get_json_output(call_response, json_mode=False)
        == '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    )

    completion.content[0] = ToolUseBlock(
        id="id", input=None, name="FormatBook", type="tool_use"
    )

    with pytest.raises(
        ValueError, match="No tool call or JSON object found in response."
    ):
        get_json_output(call_response, json_mode=False)


def test_get_json_output_call_response_chunk() -> None:
    """Tests the `get_json_output` function with a call response chunk."""
    tool_call = InputJSONDelta(
        type="input_json_delta",
        partial_json='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
    )
    chunk = RawContentBlockDeltaEvent(
        index=0,
        delta=TextDelta(
            text="json_output",
            type="text_delta",
        ),
        type="content_block_delta",
    )
    call_response_chunk = AnthropicCallResponseChunk(chunk=chunk)
    assert get_json_output(call_response_chunk, json_mode=True) == "json_output"
    chunk.delta = tool_call
    assert (
        get_json_output(call_response_chunk, json_mode=False)
        == '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    )
    chunk.delta = TextDelta(
        type="text_delta",
        text="",
    )

    assert get_json_output(call_response_chunk, json_mode=False) == ""
