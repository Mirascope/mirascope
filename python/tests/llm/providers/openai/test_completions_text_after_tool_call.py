"""Tests for streamed text that arrives after a tool call."""

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
    delta: dict[str, Any], finish_reason: str | None = None
) -> ChatCompletionChunk:
    return ChatCompletionChunk.construct(
        id="fixture-stream",
        created=1,
        model="qwen3",
        object="chat.completion.chunk",
        choices=[{"index": 0, "delta": delta, "finish_reason": finish_reason}],
    )


def tool_delta(id: str, city: str, index: int) -> dict[str, Any]:
    return {
        "tool_calls": [
            {
                "index": index,
                "id": id,
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": f'{{"city": "{city}"}}',
                },
            }
        ]
    }


def stream_content(chunks: Sequence[ChatCompletionChunk]) -> list[tuple[str, str]]:
    model = llm.Model("openai/qwen3:completions")
    with patch(
        "openai.resources.chat.completions.Completions.create",
        return_value=iter(chunks),
    ):
        response = model.stream("Weather in Paris?", tools=[get_weather])
        response.finish()
    content: list[tuple[str, str]] = []
    for part in response.content:
        if isinstance(part, llm.Text):
            content.append(("text", part.text))
        elif isinstance(part, llm.ToolCall):
            content.append(("tool_call", part.args))
    return content


def test_stream_text_after_tool_call() -> None:
    """vLLM and SGLang stream text the model writes after a tool call as content."""
    assert stream_content(
        [
            make_chunk(tool_delta("call_paris", "Paris", 0)),
            make_chunk({"content": "Checking the weather."}),
            make_chunk({}, finish_reason="tool_calls"),
        ]
    ) == [
        ("tool_call", '{"city": "Paris"}'),
        ("text", "Checking the weather."),
    ]


def test_stream_tool_call_after_text_after_tool_call() -> None:
    assert stream_content(
        [
            make_chunk(tool_delta("call_paris", "Paris", 0)),
            make_chunk({"content": "And London:"}),
            make_chunk(tool_delta("call_london", "London", 1)),
            make_chunk({}, finish_reason="tool_calls"),
        ]
    ) == [
        ("tool_call", '{"city": "Paris"}'),
        ("text", "And London:"),
        ("tool_call", '{"city": "London"}'),
    ]
