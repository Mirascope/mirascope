"""Anthropic response decoding."""

import json

from anthropic import types as anthropic_types
from anthropic.lib.streaming import AsyncMessageStreamManager, MessageStreamManager

from ....content import (
    AssistantContentPart,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    Thought,
    ThoughtChunk,
    ThoughtEndChunk,
    ThoughtStartChunk,
    ToolCall,
    ToolCallChunk,
    ToolCallEndChunk,
    ToolCallStartChunk,
)
from ....messages import AssistantMessage
from ....responses import (
    AsyncChunkIterator,
    ChunkIterator,
    FinishReason,
    FinishReasonChunk,
    RawStreamEventChunk,
)
from ..model_ids import AnthropicModelId

ANTHROPIC_FINISH_REASON_MAP = {
    "max_tokens": FinishReason.MAX_TOKENS,
    "refusal": FinishReason.REFUSAL,
}


def _decode_assistant_content(
    content: anthropic_types.ContentBlock,
) -> AssistantContentPart:
    """Convert Anthropic content block to mirascope AssistantContentPart."""
    if content.type == "text":
        return Text(text=content.text)
    elif content.type == "tool_use":
        return ToolCall(
            id=content.id,
            name=content.name,
            args=json.dumps(content.input),
        )
    elif content.type == "thinking":
        return Thought(thought=content.thinking)
    else:
        raise NotImplementedError(
            f"Support for content type `{content.type}` is not yet implemented."
        )


def decode_response(
    response: anthropic_types.Message,
    model_id: AnthropicModelId,
) -> tuple[AssistantMessage, FinishReason | None]:
    """Convert Anthropic message to mirascope AssistantMessage."""
    assistant_message = AssistantMessage(
        content=[_decode_assistant_content(part) for part in response.content],
        provider="anthropic",
        model_id=model_id,
        raw_content=[part.model_dump() for part in response.content],
    )
    finish_reason = (
        ANTHROPIC_FINISH_REASON_MAP.get(response.stop_reason)
        if response.stop_reason
        else None
    )
    return assistant_message, finish_reason


class _AnthropicChunkProcessor:
    """Processes Anthropic stream events and maintains state across events."""

    def __init__(self) -> None:
        self.current_block_type: str | None = None

    def process_event(
        self, event: anthropic_types.RawMessageStreamEvent
    ) -> ChunkIterator:
        """Process a single Anthropic event and yield the appropriate content chunks."""
        yield RawStreamEventChunk(raw_stream_event=event)

        if event.type == "content_block_start":
            content_block = event.content_block
            self.current_block_type = content_block.type

            if content_block.type == "text":
                yield TextStartChunk()
            elif content_block.type == "tool_use":
                yield ToolCallStartChunk(
                    id=content_block.id,
                    name=content_block.name,
                )
            elif content_block.type == "thinking":
                yield ThoughtStartChunk()
            else:
                raise NotImplementedError

        elif event.type == "content_block_delta":
            delta = event.delta
            if delta.type == "text_delta":
                yield TextChunk(delta=delta.text)
            elif delta.type == "input_json_delta":
                yield ToolCallChunk(delta=delta.partial_json)
            elif delta.type == "thinking_delta":
                yield ThoughtChunk(delta=delta.thinking)
            elif delta.type == "signature_delta":
                pass
            else:
                raise NotImplementedError

        elif event.type == "content_block_stop":
            if self.current_block_type == "text":
                yield TextEndChunk()
            elif self.current_block_type == "tool_use":
                yield ToolCallEndChunk()
            elif self.current_block_type == "thinking":
                yield ThoughtEndChunk()
            else:
                raise NotImplementedError

            self.current_block_type = None

        elif event.type == "message_delta":
            if event.delta.stop_reason:
                finish_reason = ANTHROPIC_FINISH_REASON_MAP.get(event.delta.stop_reason)
                if finish_reason is not None:
                    yield FinishReasonChunk(finish_reason=finish_reason)


def decode_stream(
    anthropic_stream_manager: MessageStreamManager,
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an Anthropic MessageStreamManager"""
    processor = _AnthropicChunkProcessor()
    with anthropic_stream_manager as stream:
        for event in stream._raw_stream:
            yield from processor.process_event(event)


async def decode_async_stream(
    anthropic_stream_manager: AsyncMessageStreamManager,
) -> AsyncChunkIterator:
    """Returns an AsyncChunkIterator converted from an Anthropic MessageStreamManager"""
    processor = _AnthropicChunkProcessor()
    async with anthropic_stream_manager as stream:
        async for event in stream._raw_stream:
            for item in processor.process_event(event):
                yield item
