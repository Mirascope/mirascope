"""Beta Anthropic response decoding."""

import json
from typing import Any, TypeAlias, cast

from anthropic.lib.streaming._beta_messages import (
    BetaAsyncMessageStreamManager,
    BetaMessageStreamManager,
)
from anthropic.types.beta import (
    BetaContentBlock,
    BetaRawMessageStreamEvent,
    BetaRedactedThinkingBlockParam,
    BetaTextBlockParam,
    BetaThinkingBlockParam,
    BetaToolUseBlockParam,
)
from anthropic.types.beta.parsed_beta_message import ParsedBetaMessage

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
    RawMessageChunk,
    RawStreamEventChunk,
    Usage,
    UsageDeltaChunk,
)
from ..model_id import model_name
from .decode import decode_usage

BETA_FINISH_REASON_MAP = {
    "max_tokens": FinishReason.MAX_TOKENS,
    "refusal": FinishReason.REFUSAL,
    "model_context_window_exceeded": FinishReason.CONTEXT_LENGTH_EXCEEDED,
}


def _decode_beta_assistant_content(content: BetaContentBlock) -> AssistantContentPart:
    """Convert Beta content block to mirascope AssistantContentPart."""
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
            f"Support for beta content type `{content.type}` is not yet implemented."
        )


def beta_decode_response(
    response: ParsedBetaMessage[Any],
    model_id: str,
) -> tuple[AssistantMessage, FinishReason | None, Usage]:
    """Convert Beta message to mirascope AssistantMessage and usage."""
    assistant_message = AssistantMessage(
        content=[_decode_beta_assistant_content(part) for part in response.content],
        provider_id="anthropic",
        model_id=model_id,
        provider_model_name=model_name(model_id),
        raw_message={
            "role": response.role,
            "content": [
                part.model_dump(exclude_none=True) for part in response.content
            ],
        },
    )
    finish_reason = (
        BETA_FINISH_REASON_MAP.get(response.stop_reason)
        if response.stop_reason
        else None
    )
    usage = decode_usage(response.usage)
    return assistant_message, finish_reason, usage


BetaContentBlockParam: TypeAlias = (
    BetaTextBlockParam
    | BetaThinkingBlockParam
    | BetaToolUseBlockParam
    | BetaRedactedThinkingBlockParam
)


class _BetaChunkProcessor:
    """Processes Beta stream events and maintains state across events."""

    def __init__(self) -> None:
        self.current_block_param: BetaContentBlockParam | None = None
        self.accumulated_tool_json: str = ""
        self.accumulated_blocks: list[BetaContentBlockParam] = []

    def process_event(self, event: BetaRawMessageStreamEvent) -> ChunkIterator:
        """Process a single Beta event and yield the appropriate content chunks."""
        yield RawStreamEventChunk(raw_stream_event=event)

        if event.type == "content_block_start":
            content_block = event.content_block

            if content_block.type == "text":
                self.current_block_param = {
                    "type": "text",
                    "text": content_block.text,
                }
                yield TextStartChunk()
            elif content_block.type == "tool_use":
                self.current_block_param = {
                    "type": "tool_use",
                    "id": content_block.id,
                    "name": content_block.name,
                    "input": {},
                }
                self.accumulated_tool_json = ""
                yield ToolCallStartChunk(
                    id=content_block.id,
                    name=content_block.name,
                )
            elif content_block.type == "thinking":
                self.current_block_param = {
                    "type": "thinking",
                    "thinking": "",
                    "signature": "",
                }
                yield ThoughtStartChunk()
            elif content_block.type == "redacted_thinking":  # pragma: no cover
                self.current_block_param = {
                    "type": "redacted_thinking",
                    "data": content_block.data,
                }
            else:
                raise NotImplementedError(
                    f"Support for beta content block type `{content_block.type}` "
                    "is not yet implemented."
                )

        elif event.type == "content_block_delta":
            if self.current_block_param is None:  # pragma: no cover
                raise RuntimeError("Received delta without a current block")

            delta = event.delta
            if delta.type == "text_delta":
                if self.current_block_param["type"] != "text":  # pragma: no cover
                    raise RuntimeError(
                        f"Received text_delta for {self.current_block_param['type']} block"
                    )
                self.current_block_param["text"] += delta.text
                yield TextChunk(delta=delta.text)
            elif delta.type == "input_json_delta":
                if self.current_block_param["type"] != "tool_use":  # pragma: no cover
                    raise RuntimeError(
                        f"Received input_json_delta for {self.current_block_param['type']} block"
                    )
                self.accumulated_tool_json += delta.partial_json
                yield ToolCallChunk(delta=delta.partial_json)
            elif delta.type == "thinking_delta":
                if self.current_block_param["type"] != "thinking":  # pragma: no cover
                    raise RuntimeError(
                        f"Received thinking_delta for {self.current_block_param['type']} block"
                    )
                self.current_block_param["thinking"] += delta.thinking
                yield ThoughtChunk(delta=delta.thinking)
            elif delta.type == "signature_delta":
                if self.current_block_param["type"] != "thinking":  # pragma: no cover
                    raise RuntimeError(
                        f"Received signature_delta for {self.current_block_param['type']} block"
                    )
                self.current_block_param["signature"] += delta.signature
            else:
                raise RuntimeError(
                    f"Received unsupported delta type: {delta.type}"
                )  # pragma: no cover

        elif event.type == "content_block_stop":
            if self.current_block_param is None:  # pragma: no cover
                raise RuntimeError("Received stop without a current block")

            block_type = self.current_block_param["type"]

            if block_type == "text":
                yield TextEndChunk()
            elif block_type == "tool_use":
                if self.current_block_param["type"] != "tool_use":  # pragma: no cover
                    raise RuntimeError(
                        f"Block type mismatch: stored {self.current_block_param['type']}, expected tool_use"
                    )
                self.current_block_param["input"] = (
                    json.loads(self.accumulated_tool_json)
                    if self.accumulated_tool_json
                    else {}
                )
                yield ToolCallEndChunk()
            elif block_type == "thinking":
                yield ThoughtEndChunk()
            else:
                raise NotImplementedError

            self.accumulated_blocks.append(self.current_block_param)
            self.current_block_param = None

        elif event.type == "message_delta":
            if event.delta.stop_reason:
                finish_reason = BETA_FINISH_REASON_MAP.get(event.delta.stop_reason)
                if finish_reason is not None:
                    yield FinishReasonChunk(finish_reason=finish_reason)

            # Emit usage delta
            usage = event.usage
            yield UsageDeltaChunk(
                input_tokens=usage.input_tokens or 0,
                output_tokens=usage.output_tokens,
                cache_read_tokens=usage.cache_read_input_tokens or 0,
                cache_write_tokens=usage.cache_creation_input_tokens or 0,
                reasoning_tokens=0,
            )

    def raw_message_chunk(self) -> RawMessageChunk:
        return RawMessageChunk(
            raw_message=cast(
                dict[str, Any],
                {
                    "role": "assistant",
                    "content": self.accumulated_blocks,
                },
            )
        )


def beta_decode_stream(
    beta_stream_manager: BetaMessageStreamManager[Any],
) -> ChunkIterator:
    """Returns a ChunkIterator converted from a Beta MessageStreamManager."""
    processor = _BetaChunkProcessor()
    with beta_stream_manager as stream:
        for event in stream._raw_stream:  # pyright: ignore[reportPrivateUsage]
            yield from processor.process_event(event)
    yield processor.raw_message_chunk()


async def beta_decode_async_stream(
    beta_stream_manager: BetaAsyncMessageStreamManager[Any],
) -> AsyncChunkIterator:
    """Returns an AsyncChunkIterator converted from a Beta MessageStreamManager."""
    processor = _BetaChunkProcessor()
    async with beta_stream_manager as stream:
        async for event in stream._raw_stream:  # pyright: ignore[reportPrivateUsage]
            for item in processor.process_event(event):
                yield item
    yield processor.raw_message_chunk()
