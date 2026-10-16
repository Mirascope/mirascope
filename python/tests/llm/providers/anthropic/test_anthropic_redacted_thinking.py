"""Tests that redacted thinking blocks are decoded instead of raising.

Anthropic returns a `redacted_thinking` block when part of the model's reasoning
is redacted. It carries no readable text, so it is left out of the decoded content
and kept in `raw_message`, which is what gets sent back on the next turn.
"""

from anthropic import types as anthropic_types
from anthropic.types import beta as beta_types
from anthropic.types.beta.parsed_beta_message import ParsedBetaMessage

from mirascope.llm.providers.anthropic._utils import beta_decode, decode

REDACTED_DATA = "RW5jcnlwdGVkIHRoaW5raW5n"


def _message() -> anthropic_types.Message:
    return anthropic_types.Message(
        id="msg_1",
        type="message",
        role="assistant",
        model="claude-sonnet-4-5",
        content=[
            anthropic_types.RedactedThinkingBlock(
                type="redacted_thinking", data=REDACTED_DATA
            ),
            anthropic_types.TextBlock(type="text", text="Here is the answer."),
        ],
        stop_reason="end_turn",
        stop_sequence=None,
        usage=anthropic_types.Usage(input_tokens=10, output_tokens=5),
    )


def test_decode_response_skips_redacted_thinking() -> None:
    assistant_message, _, _ = decode.decode_response(
        _message(), "anthropic/claude-sonnet-4-5", include_thoughts=True
    )

    assert [part.type for part in assistant_message.content] == ["text"]


def test_decode_stream_keeps_redacted_thinking_in_raw_message() -> None:
    processor = decode._AnthropicChunkProcessor(include_thoughts=True)  # pyright: ignore[reportPrivateUsage]
    events = [
        anthropic_types.RawContentBlockStartEvent(
            type="content_block_start",
            index=0,
            content_block=anthropic_types.RedactedThinkingBlock(
                type="redacted_thinking", data=REDACTED_DATA
            ),
        ),
        anthropic_types.RawContentBlockStopEvent(type="content_block_stop", index=0),
    ]

    for event in events:
        list(processor.process_event(event))

    assert processor.accumulated_blocks == [
        {"type": "redacted_thinking", "data": REDACTED_DATA}
    ]


def test_beta_decode_response_skips_redacted_thinking() -> None:
    message = ParsedBetaMessage[object].model_validate(_message().model_dump())

    assistant_message, _, _ = beta_decode.beta_decode_response(
        message, "anthropic-beta/claude-sonnet-4-5", include_thoughts=True
    )

    assert [part.type for part in assistant_message.content] == ["text"]


def test_beta_decode_stream_keeps_redacted_thinking_in_raw_message() -> None:
    processor = beta_decode._BetaChunkProcessor(include_thoughts=True)  # pyright: ignore[reportPrivateUsage]
    events = [
        beta_types.BetaRawContentBlockStartEvent(
            type="content_block_start",
            index=0,
            content_block=beta_types.BetaRedactedThinkingBlock(
                type="redacted_thinking", data=REDACTED_DATA
            ),
        ),
        beta_types.BetaRawContentBlockStopEvent(type="content_block_stop", index=0),
    ]

    for event in events:
        list(processor.process_event(event))

    assert processor.accumulated_blocks == [
        {"type": "redacted_thinking", "data": REDACTED_DATA}
    ]
