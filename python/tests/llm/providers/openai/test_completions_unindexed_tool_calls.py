"""Tests for streamed tool calls that arrive without an index."""

from collections.abc import Sequence
from typing import Any
from unittest.mock import patch

from openai.types.chat import ChatCompletionChunk

from mirascope import llm


@llm.tool
def get_weather(city: str) -> str:
    """Return the weather of a city."""
    return f"{city}: cloudy"


def make_chunk(
    tool_calls: Sequence[dict[str, Any]], finish_reason: str | None = None
) -> ChatCompletionChunk:
    # The openai client builds streamed chunks without validating them, so a
    # tool call delta the server sent without an index has `index=None`.
    return ChatCompletionChunk.construct(
        id="fixture-stream",
        created=1,
        model="gemini-3.5-flash",
        object="chat.completion.chunk",
        choices=[
            {
                "index": 0,
                "delta": {"tool_calls": list(tool_calls) or None},
                "finish_reason": finish_reason,
            }
        ],
    )


def tool_delta(
    id: str | None, name: str | None, arguments: str, index: int | None = None
) -> dict[str, Any]:
    return {
        **({"index": index} if index is not None else {}),
        "id": id,
        "type": "function" if id else None,
        "function": {"name": name, "arguments": arguments},
    }


def stream_tool_calls(chunks: Sequence[ChatCompletionChunk]) -> list[tuple[str, str]]:
    model = llm.Model("openai/gemini-3.5-flash:completions")
    with patch(
        "openai.resources.chat.completions.Completions.create",
        return_value=iter(chunks),
    ):
        response = model.stream("Weather in Paris and London?", tools=[get_weather])
        response.finish()
    return [(tool_call.id, tool_call.args) for tool_call in response.tool_calls]


def test_stream_whole_tool_calls_without_index() -> None:
    """Gemini's OpenAI-compatible endpoint sends each parallel call whole, without an index."""
    assert stream_tool_calls(
        [
            make_chunk([tool_delta("call_paris", "get_weather", '{"city": "Paris"}')]),
            make_chunk(
                [tool_delta("call_london", "get_weather", '{"city": "London"}')]
            ),
            make_chunk([], finish_reason="tool_calls"),
        ]
    ) == [
        ("call_paris", '{"city": "Paris"}'),
        ("call_london", '{"city": "London"}'),
    ]


def test_stream_tool_call_fragments_without_index_continue_the_last_call() -> None:
    assert stream_tool_calls(
        [
            make_chunk([tool_delta("call_paris", "get_weather", '{"city": ')]),
            make_chunk([tool_delta("call_paris", None, '"Paris"}')]),
            make_chunk([tool_delta("call_london", "get_weather", '{"ci')]),
            make_chunk([tool_delta(None, None, 'ty": "London"}')]),
            make_chunk([], finish_reason="tool_calls"),
        ]
    ) == [
        ("call_paris", '{"city": "Paris"}'),
        ("call_london", '{"city": "London"}'),
    ]


def test_stream_tool_calls_with_one_reused_index_remain_separate() -> None:
    assert stream_tool_calls(
        [
            make_chunk(
                [
                    tool_delta("call_paris", "get_weather", '{"city": "Paris"}', 0),
                    tool_delta("call_london", "get_weather", '{"city": ', 0),
                ]
            ),
            make_chunk([tool_delta(None, None, '"London"}', 0)]),
            make_chunk(
                [tool_delta("call_berlin", "get_weather", '{"city": "Berlin"}', 1)]
            ),
            make_chunk([], finish_reason="tool_calls"),
        ]
    ) == [
        ("call_paris", '{"city": "Paris"}'),
        ("call_london", '{"city": "London"}'),
        ("call_berlin", '{"city": "Berlin"}'),
    ]
