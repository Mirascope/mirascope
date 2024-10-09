"""Tests the `bedrock._utils.get_json_output` module."""

from typing import Any, cast

import pytest

from mirascope.core.bedrock._types import StreamOutputChunk
from mirascope.core.bedrock._utils._get_json_output import get_json_output
from mirascope.core.bedrock.call_params import BedrockCallParams
from mirascope.core.bedrock.call_response import BedrockCallResponse
from mirascope.core.bedrock.call_response_chunk import BedrockCallResponseChunk


def test_get_json_output_call_response() -> None:
    """Tests the `get_json_output` function with a call response."""
    message: dict[str, Any] = {
        "role": "assistant",
        "content": [
            {
                "text": '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            }
        ],
    }
    call_response = BedrockCallResponse(
        metadata={},  # pyright: ignore [reportArgumentType]
        response={  # pyright: ignore [reportArgumentType]
            "output": {"message": message},
        },
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        call_params=BedrockCallParams(max_tokens=1000),  # pyright: ignore [reportCallIssue]
        call_kwargs={},  # pyright: ignore [reportArgumentType]
        user_message_param=None,
        start_time=0,
        end_time=0,
        messages=[],
    )
    assert (
        get_json_output(call_response, json_mode=True)
        == '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    )

    message["content"] = [
        {
            "type": "toolUse",
            "toolUse": {
                "input": {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
            },
        }
    ]
    assert (
        get_json_output(call_response, json_mode=False)
        == '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    )

    message["content"] = [{"type": "toolUse", "toolUse": {}}]
    with pytest.raises(
        ValueError, match="No tool call or JSON object found in response."
    ):
        get_json_output(call_response, json_mode=False)

    # Test case for empty message content
    message["content"] = []
    with pytest.raises(
        ValueError, match="No tool call or JSON object found in response."
    ):
        get_json_output(call_response, json_mode=False)

    # Test case for missing message
    call_response.response = {"output": {}}  # pyright: ignore [reportAttributeAccessIssue]
    with pytest.raises(
        ValueError, match="No tool call or JSON object found in response."
    ):
        get_json_output(call_response, json_mode=False)


def test_get_json_output_call_response_chunk() -> None:
    """Tests the `get_json_output` function with a call response chunk."""
    chunk = {
        "contentBlockDelta": {
            "delta": {
                "text": "json_output",
            }
        }
    }
    call_response_chunk = BedrockCallResponseChunk(chunk=chunk)  # pyright: ignore [reportArgumentType]
    assert get_json_output(call_response_chunk, json_mode=True) == "json_output"

    chunk["contentBlockDelta"]["delta"] = {  # pyright: ignore [reportArgumentType]
        "toolUse": {
            "input": '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
        }
    }
    assert (
        get_json_output(call_response_chunk, json_mode=False)
        == '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    )

    chunk["contentBlockDelta"]["delta"] = {"text": ""}
    assert get_json_output(call_response_chunk, json_mode=False) == ""

    # Test case for missing contentBlockDelta
    chunk = cast(StreamOutputChunk, {})
    call_response_chunk = BedrockCallResponseChunk(chunk=chunk)
    assert get_json_output(call_response_chunk, json_mode=False) == ""

    # Test case for missing delta in contentBlockDelta
    chunk = cast(StreamOutputChunk, {"contentBlockDelta": {}})
    call_response_chunk = BedrockCallResponseChunk(chunk=chunk)
    assert get_json_output(call_response_chunk, json_mode=False) == ""
