"""Tests for parallel function calls in OpenAI Responses streams."""

from typing import Any
from unittest.mock import patch

from openai.types.responses import Response, ResponseStreamEvent
from pydantic import TypeAdapter

from mirascope import llm

_EVENT_ADAPTER: TypeAdapter[ResponseStreamEvent] = TypeAdapter(ResponseStreamEvent)


@llm.tool
def get_weather(city: str) -> str:
    """Return the weather for a city."""
    return f"{city}: cloudy"


@llm.tool
def get_time(tz: str) -> str:
    """Return the current time in a timezone."""
    return f"{tz}: noon"


def _response_payload() -> dict[str, Any]:
    return {
        "id": "resp_parallel",
        "object": "response",
        "created_at": 1,
        "status": "completed",
        "model": "gpt-5.6-terra",
        "output": [
            {
                "id": "fc_weather",
                "type": "function_call",
                "call_id": "call_weather",
                "name": "get_weather",
                "arguments": '{"city": "Paris"}',
                "status": "completed",
            },
            {
                "id": "fc_time",
                "type": "function_call",
                "call_id": "call_time",
                "name": "get_time",
                "arguments": '{"tz": "UTC"}',
                "status": "completed",
            },
        ],
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "usage": {
            "input_tokens": 10,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens": 20,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 30,
        },
    }


def _events() -> list[ResponseStreamEvent]:
    raw_events: list[dict[str, Any]] = [
        {
            "type": "response.output_item.added",
            "sequence_number": 1,
            "output_index": 0,
            "item": {
                "id": "fc_weather",
                "type": "function_call",
                "call_id": "call_weather",
                "name": "get_weather",
                "arguments": "",
                "status": "in_progress",
            },
        },
        {
            "type": "response.output_item.added",
            "sequence_number": 2,
            "output_index": 1,
            "item": {
                "id": "fc_time",
                "type": "function_call",
                "call_id": "call_time",
                "name": "get_time",
                "arguments": "",
                "status": "in_progress",
            },
        },
        {
            "type": "response.function_call_arguments.delta",
            "sequence_number": 3,
            "item_id": "fc_weather",
            "output_index": 0,
            "delta": '{"city":',
        },
        {
            "type": "response.function_call_arguments.delta",
            "sequence_number": 4,
            "item_id": "fc_time",
            "output_index": 1,
            "delta": '{"tz":',
        },
        {
            "type": "response.function_call_arguments.delta",
            "sequence_number": 5,
            "item_id": "fc_weather",
            "output_index": 0,
            "delta": '"Paris"}',
        },
        {
            "type": "response.function_call_arguments.delta",
            "sequence_number": 6,
            "item_id": "fc_time",
            "output_index": 1,
            "delta": '"UTC"}',
        },
        {
            "type": "response.function_call_arguments.done",
            "sequence_number": 7,
            "item_id": "fc_time",
            "output_index": 1,
            "name": "get_time",
            "arguments": '{"tz": "UTC"}',
        },
        {
            "type": "response.function_call_arguments.done",
            "sequence_number": 8,
            "item_id": "fc_weather",
            "output_index": 0,
            "name": "get_weather",
            "arguments": '{"city": "Paris"}',
        },
        {
            "type": "response.completed",
            "sequence_number": 9,
            "response": Response.model_validate(_response_payload()).model_dump(
                mode="json"
            ),
        },
    ]
    return [_EVENT_ADAPTER.validate_python(event) for event in raw_events]


def test_interleaved_parallel_tool_calls_keep_their_ids_and_args() -> None:
    """Argument deltas identify their call by item_id, not by the last added item."""
    model = llm.Model("openai/gpt-5.6-terra:responses")
    with patch(
        "openai.resources.responses.Responses.create", return_value=iter(_events())
    ):
        response = model.stream(
            "Weather in Paris and time in UTC?", tools=[get_weather, get_time]
        )
        response.finish()

    assert [(tool.id, tool.name, tool.args) for tool in response.tool_calls] == [
        ("call_time", "get_time", '{"tz":"UTC"}'),
        ("call_weather", "get_weather", '{"city":"Paris"}'),
    ]
