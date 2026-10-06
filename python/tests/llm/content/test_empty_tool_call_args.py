"""Regression: empty OpenAI tool arguments must not break execute/encode (#2883)."""

from __future__ import annotations

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_function_tool_call import (
    ChatCompletionMessageFunctionToolCall,
    Function,
)
from openai.types.completion_usage import CompletionUsage
from openai.types.responses import (
    Response,
    ResponseFunctionToolCall,
    ResponseUsage,
)

from mirascope import llm
from mirascope.llm.content import (
    Text,
    ToolCall,
    ToolOutput,
    normalize_tool_call_args,
    parse_tool_call_args,
)
from mirascope.llm.messages import AssistantMessage, UserMessage
from mirascope.llm.providers.anthropic._utils.encode import (
    encode_request as anth_encode,
)
from mirascope.llm.providers.google._utils.encode import encode_request as goog_encode
from mirascope.llm.providers.openai.completions._utils.decode import (
    decode_response as decode_completions,
)
from mirascope.llm.providers.openai.responses._utils.decode import (
    decode_response as decode_responses,
)
from mirascope.llm.tools import Toolkit


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("", "{}"),
        ("   ", "{}"),
        (None, "{}"),
        ("{}", "{}"),
        ('{"a": 1}', '{"a": 1}'),
    ],
)
def test_normalize_tool_call_args(raw: str | None, expected: str) -> None:
    assert normalize_tool_call_args(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", None])
def test_parse_tool_call_args_empty(raw: str | None) -> None:
    assert parse_tool_call_args(raw) == {}


def test_parse_tool_call_args_object() -> None:
    assert parse_tool_call_args('{"x": 1}') == {"x": 1}


def _openai_completion_with_args(arguments: str) -> ChatCompletion:
    tc = ChatCompletionMessageFunctionToolCall(
        id="call_empty",
        type="function",
        function=Function(name="ping", arguments=arguments),
    )
    msg = ChatCompletionMessage(role="assistant", content=None, tool_calls=[tc])
    choice = Choice(index=0, message=msg, finish_reason="tool_calls")
    return ChatCompletion(
        id="chatcmpl-1",
        choices=[choice],
        created=1,
        model="gpt-4o",
        object="chat.completion",
        usage=CompletionUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
    )


@llm.tool
def ping() -> str:
    """No-arg health check."""
    return "pong"


def test_openai_completions_decode_normalizes_empty_args() -> None:
    asst, _, _ = decode_completions(
        _openai_completion_with_args(""), "openai/gpt-4o", "openai"
    )
    assert isinstance(asst.content[0], ToolCall)
    assert asst.content[0].args == "{}"
    out = ping.execute(asst.content[0])
    assert out.error is None
    assert out.result == "pong"


def test_openai_responses_decode_normalizes_empty_args() -> None:
    response = Response(
        id="resp_1",
        created_at=1.0,
        model="gpt-4o",
        object="response",
        output=[
            ResponseFunctionToolCall(
                type="function_call",
                call_id="call_empty",
                name="ping",
                arguments="",
                id="fc_1",
                status="completed",
            )
        ],
        parallel_tool_calls=False,
        tool_choice="auto",
        tools=[],
        usage=ResponseUsage(
            input_tokens=1,
            output_tokens=1,
            total_tokens=2,
            input_tokens_details={"cached_tokens": 0},
            output_tokens_details={"reasoning_tokens": 0},
        ),
        status="completed",
    )
    asst, _, _ = decode_responses(
        response, "openai/gpt-4o", "openai", include_thoughts=False
    )
    assert isinstance(asst.content[0], ToolCall)
    assert asst.content[0].args == "{}"


def test_anthropic_and_google_encode_empty_tool_args() -> None:
    """History with empty tool args must encode without JSONDecodeError."""
    asst = AssistantMessage(
        content=[ToolCall(id="call_empty", name="ping", args="")],
        provider_id="openai",
        model_id="openai/gpt-4o",
        provider_model_name="gpt-4o",
        raw_message=None,
    )
    history = [
        UserMessage(content=[Text(text="ping")]),
        asst,
        UserMessage(content=[ToolOutput(id="call_empty", name="ping", result="pong")]),
    ]
    _, _, anth_kwargs = anth_encode(
        model_id="anthropic/claude-sonnet-4-5",
        messages=history,
        tools=Toolkit([ping]),
        format=None,
        params={},
    )
    # Find tool_use block with empty input
    found = False
    for msg in anth_kwargs["messages"]:
        for block in msg.get("content", []):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                assert block["input"] == {}
                found = True
    assert found

    _, _, goog_kwargs = goog_encode(
        model_id="google/gemini-2.5-flash",
        messages=history,
        tools=Toolkit([ping]),
        format=None,
        params={},
    )
    found = False
    for content in goog_kwargs["contents"]:
        for part in content.get("parts", []):
            fc = part.get("function_call") if isinstance(part, dict) else None
            if fc:
                assert fc.get("args") == {}
                found = True
    assert found
