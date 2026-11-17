"""Tests for Responses streams that end with `response.incomplete`."""

from unittest.mock import patch

from openai.types.responses import Response, ResponseStreamEvent
from pydantic import TypeAdapter

from mirascope import llm

_EVENT_ADAPTER: TypeAdapter[ResponseStreamEvent] = TypeAdapter(ResponseStreamEvent)


def _response_payload() -> dict[str, object]:
    return {
        "id": "resp_1",
        "object": "response",
        "created_at": 1,
        "status": "incomplete",
        "error": None,
        "incomplete_details": {"reason": "max_output_tokens"},
        "model": "gpt-5.6-terra",
        "output": [
            {
                "id": "msg_1",
                "type": "message",
                "role": "assistant",
                "status": "incomplete",
                "content": [{"type": "output_text", "annotations": [], "text": "Hi"}],
            }
        ],
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "usage": {
            "input_tokens": 14,
            "input_tokens_details": {"cached_tokens": 8},
            "output_tokens": 50,
            "output_tokens_details": {"reasoning_tokens": 20},
            "total_tokens": 64,
        },
    }


def test_incomplete_stream_keeps_usage_and_raw_message() -> None:
    """`response.incomplete` carries the usage and output, like `response.completed`."""
    events = [
        _EVENT_ADAPTER.validate_python(event)
        for event in (
            {
                "type": "response.output_text.delta",
                "sequence_number": 1,
                "item_id": "msg_1",
                "output_index": 0,
                "content_index": 0,
                "delta": "Hi",
                "logprobs": [],
            },
            {
                "type": "response.output_text.done",
                "sequence_number": 2,
                "item_id": "msg_1",
                "output_index": 0,
                "content_index": 0,
                "text": "Hi",
                "logprobs": [],
            },
            {
                "type": "response.incomplete",
                "sequence_number": 3,
                "response": _response_payload(),
            },
        )
    ]
    assert Response.model_validate(_response_payload()).usage is not None

    model = llm.Model("openai/gpt-5.6-terra:responses")
    with patch(
        "openai.resources.responses.Responses.create", return_value=iter(events)
    ):
        response = model.stream("Say hi")
        response.finish()

    assert response.finish_reason == llm.FinishReason.MAX_TOKENS
    assert response.usage is not None
    assert response.usage.input_tokens == 14
    assert response.usage.output_tokens == 50
    assert response.usage.cache_read_tokens == 8
    assert response.usage.reasoning_tokens == 20
