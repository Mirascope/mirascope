"""Tests the `fallback` module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic import RateLimitError as AnthropicRateLimitError
from anthropic.types import (
    Message,
    MessageDeltaUsage,
    RawContentBlockDeltaEvent,
    RawContentBlockStartEvent,
    RawContentBlockStopEvent,
    RawMessageDeltaEvent,
    RawMessageStartEvent,
    RawMessageStopEvent,
    TextBlock,
    TextDelta,
    Usage,
)
from anthropic.types.raw_message_delta_event import Delta
from httpx import Request, Response
from openai import RateLimitError as OpenAIRateLimitError

from mirascope import llm
from mirascope.retries.fallback import FallbackError, fallback


@patch(
    "anthropic.resources.messages.Messages.create",
    new_callable=MagicMock,
    side_effect=AnthropicRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
    side_effect=OpenAIRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
def test_fallback(mock_openai_create: MagicMock, mock_anthropic_create: MagicMock):
    @fallback(
        OpenAIRateLimitError,
        [
            {
                "catch": AnthropicRateLimitError,
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-latest",
            }
        ],
    )
    @llm.call("openai", "gpt-4o-mini")
    def answer_question(question: str) -> str:
        return question

    with pytest.raises(FallbackError):
        answer_question("What is the meaning of life?")


@patch(
    "anthropic.resources.messages.Messages.create",
    new_callable=MagicMock,
    return_value=Message(
        id="id",
        content=[TextBlock(text="content", type="text")],
        model="claude-3-5-sonnet-20240620",
        role="assistant",
        stop_reason="end_turn",
        stop_sequence=None,
        type="message",
        usage=Usage(input_tokens=1, output_tokens=1),
    ),
)
@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
    side_effect=OpenAIRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
def test_fallback_success(
    mock_openai_create: MagicMock, mock_anthropic_create: MagicMock
):
    @fallback(
        OpenAIRateLimitError,
        [
            {
                "catch": AnthropicRateLimitError,
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-latest",
            }
        ],
    )
    @llm.call("openai", "gpt-4o-mini")
    def answer_question(question: str) -> str:
        return question

    response = answer_question("What is the meaning of life?")
    assert hasattr(response, "_caught")
    assert isinstance(response._caught[0], OpenAIRateLimitError)


@patch(
    "anthropic.resources.messages.AsyncMessages.create",
    new_callable=MagicMock,
    side_effect=AnthropicRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=MagicMock,
    side_effect=OpenAIRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
@pytest.mark.asyncio
async def test_fallback_async(
    mock_openai_create: MagicMock, mock_anthropic_create: MagicMock
):
    @fallback(
        OpenAIRateLimitError,
        [
            {
                "catch": AnthropicRateLimitError,
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-latest",
            }
        ],
    )
    @llm.call("openai", "gpt-4o-mini")
    async def answer_question_async(question: str) -> str:
        return question

    with pytest.raises(FallbackError):
        await answer_question_async("What is the meaning of life?")


@patch(
    "anthropic.resources.messages.AsyncMessages.create",
    new_callable=MagicMock,
)
@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=MagicMock,
    side_effect=OpenAIRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
@pytest.mark.asyncio
async def test_fallback_async_success(
    mock_openai_call: AsyncMock, mock_anthropic_create: MagicMock
):
    async def awaitable_message():
        return Message(
            id="id",
            content=[TextBlock(text="content", type="text")],
            model="claude-3-5-sonnet-20240620",
            role="assistant",
            stop_reason="end_turn",
            stop_sequence=None,
            type="message",
            usage=Usage(input_tokens=1, output_tokens=1),
        )

    mock_anthropic_create.return_value = awaitable_message()

    @fallback(
        OpenAIRateLimitError,
        [
            {
                "catch": AnthropicRateLimitError,
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-latest",
            }
        ],
    )
    @llm.call("openai", "gpt-4o-mini")
    async def answer_question(question: str) -> str:
        return question

    response = await answer_question("What is the meaning of life?")
    assert hasattr(response, "_caught")
    assert isinstance(response._caught[0], OpenAIRateLimitError)


@patch(
    "anthropic.resources.messages.Messages.create",
    new_callable=MagicMock,
)
@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_fallback_streaming_wrapper(
    mock_openai_create: MagicMock, mock_anthropic_create: MagicMock
) -> None:
    class StreamingError(Exception): ...

    def failing_openai_generator():
        """Generator that raises StreamingError when iterated"""
        yield MagicMock()  # This will trigger the exception when next() is called
        raise StreamingError("OpenAI streaming failed")

    mock_openai_create.return_value = failing_openai_generator()
    mock_anthropic_create.return_value = iter(
        [
            RawMessageStartEvent(
                message=Message(
                    id="msg_id",
                    content=[],
                    model="claude-3-5-sonnet-latest",
                    role="assistant",
                    stop_reason=None,
                    stop_sequence=None,
                    type="message",
                    usage=Usage(input_tokens=10, output_tokens=0),
                ),
                type="message_start",
            ),
            RawContentBlockStartEvent(
                content_block=TextBlock(
                    text="",
                    type="text",
                ),
                index=0,
                type="content_block_start",
            ),
            RawContentBlockDeltaEvent(
                delta=TextDelta(text="anthropic", type="text_delta"),
                index=0,
                type="content_block_delta",
            ),
            RawContentBlockDeltaEvent(
                delta=TextDelta(text="streamed", type="text_delta"),
                index=0,
                type="content_block_delta",
            ),
            RawContentBlockDeltaEvent(
                delta=TextDelta(text="successfully", type="text_delta"),
                index=0,
                type="content_block_delta",
            ),
            RawContentBlockStopEvent(index=0, type="content_block_stop"),
            RawMessageDeltaEvent(
                delta=Delta(stop_reason="end_turn", stop_sequence=None),
                type="message_delta",
                usage=MessageDeltaUsage(output_tokens=3),
            ),
            RawMessageStopEvent(type="message_stop"),
        ]
    )

    @llm.call("openai", "gpt-4o-mini", stream=True)
    def answer_question(question: str) -> str:
        return question

    @fallback(
        StreamingError,
        [
            {
                "catch": StreamingError,
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-latest",
            }
        ],
    )
    def answer_question_wrapper(question: str) -> list[str]:
        stream = answer_question("What is the meaning of life?")
        return [chunk.content for chunk, _ in stream if chunk.content]

    chunks = answer_question_wrapper("What is the meaning of life?")
    assert chunks == ["anthropic", "streamed", "successfully"]
