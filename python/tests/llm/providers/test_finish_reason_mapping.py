"""Tests for provider stop reasons that map to a `FinishReason`."""

import json

import httpx
import pytest
from anthropic import Anthropic, types as anthropic_types
from google.genai import types as genai_types

from mirascope import llm
from mirascope.llm.providers.anthropic._utils import decode as anthropic_decode
from mirascope.llm.providers.google._utils.decode import decode_response, decode_stream
from mirascope.llm.responses import FinishReasonChunk


def _anthropic_message(stop_reason: str) -> anthropic_types.Message:
    # The SDK does not validate the stop reason, so newer API values pass through.
    return anthropic_types.Message.model_construct(
        id="msg_1",
        type="message",
        role="assistant",
        model="claude-sonnet-4-5",
        content=[anthropic_types.TextBlock(type="text", text="partial")],
        stop_reason=stop_reason,
        stop_sequence=None,
        usage=anthropic_types.Usage(input_tokens=10, output_tokens=5),
    )


def test_anthropic_decode_response_context_window_exceeded() -> None:
    _, finish_reason, _ = anthropic_decode.decode_response(
        _anthropic_message("model_context_window_exceeded"),
        "anthropic/claude-sonnet-4-5",
        include_thoughts=False,
    )
    assert finish_reason == llm.FinishReason.CONTEXT_LENGTH_EXCEEDED


def test_anthropic_decode_stream_context_window_exceeded() -> None:
    events = [
        {
            "type": "message_start",
            "message": {
                "id": "msg_1",
                "type": "message",
                "role": "assistant",
                "model": "claude-sonnet-4-5",
                "content": [],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 10, "output_tokens": 1},
            },
        },
        {
            "type": "message_delta",
            "delta": {
                "stop_reason": "model_context_window_exceeded",
                "stop_sequence": None,
            },
            "usage": {"output_tokens": 5},
        },
        {"type": "message_stop"},
    ]
    body = "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in events)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            request=request,
            headers={"content-type": "text/event-stream"},
            content=body,
        )

    with Anthropic(
        api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))
    ) as client:
        stream = client.messages.stream(
            model="claude-sonnet-4-5", max_tokens=10, messages=[]
        )
        chunks = list(anthropic_decode.decode_stream(stream, include_thoughts=False))
    assert [c.finish_reason for c in chunks if isinstance(c, FinishReasonChunk)] == [
        llm.FinishReason.CONTEXT_LENGTH_EXCEEDED
    ]


IMAGE_REFUSALS = ["IMAGE_SAFETY", "IMAGE_PROHIBITED_CONTENT", "IMAGE_RECITATION"]


def _google_response(finish_reason: str) -> genai_types.GenerateContentResponse:
    return genai_types.GenerateContentResponse(
        candidates=[
            genai_types.Candidate(
                content=genai_types.Content(role="model", parts=[]),
                finish_reason=genai_types.FinishReason(finish_reason),
            )
        ],
        usage_metadata=genai_types.GenerateContentResponseUsageMetadata(
            prompt_token_count=3, candidates_token_count=0
        ),
    )


@pytest.mark.parametrize("reason", IMAGE_REFUSALS)
def test_google_decode_response_image_refusal(reason: str) -> None:
    _, finish_reason, _ = decode_response(
        _google_response(reason), "google/gemini-3.8-flash", include_thoughts=False
    )
    assert finish_reason == llm.FinishReason.REFUSAL


@pytest.mark.parametrize("reason", IMAGE_REFUSALS)
def test_google_decode_stream_image_refusal(reason: str) -> None:
    chunks = list(
        decode_stream(iter([_google_response(reason)]), include_thoughts=False)
    )
    assert [c.finish_reason for c in chunks if isinstance(c, FinishReasonChunk)] == [
        llm.FinishReason.REFUSAL
    ]
