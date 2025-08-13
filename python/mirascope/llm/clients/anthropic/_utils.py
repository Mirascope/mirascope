"""Anthropic message types and conversion utilities."""

import json
from collections.abc import Sequence
from functools import lru_cache

from anthropic import NotGiven
from anthropic import types as anthropic_types
from anthropic.lib.streaming import MessageStreamManager

from ...content import (
    AssistantContentPart,
    ContentPart,
    FinishReasonChunk,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    ToolCall,
)
from ...messages import AssistantMessage, Message, UserMessage, assistant
from ...responses import ChunkIterator, FinishReason
from ...tools import Tool
from ..base import _utils as _base_utils

ANTHROPIC_FINISH_REASON_MAP = {
    "end_turn": FinishReason.END_TURN,
    "max_tokens": FinishReason.MAX_TOKENS,
    "stop_sequence": FinishReason.STOP,
    "tool_use": FinishReason.TOOL_USE,
    "refusal": FinishReason.REFUSAL,
}


def _encode_content(
    content: Sequence[ContentPart],
) -> str | Sequence[anthropic_types.ContentBlockParam]:
    """Convert mirascope content to Anthropic content format."""
    if len(content) == 1 and content[0].type == "text":
        return content[0].text

    blocks: list[anthropic_types.ContentBlockParam] = []
    for part in content:
        if part.type == "text":
            blocks.append(anthropic_types.TextBlockParam(type="text", text=part.text))
        elif part.type == "tool_output":
            blocks.append(
                anthropic_types.ToolResultBlockParam(
                    type="tool_result",
                    tool_use_id=part.id,
                    content=str(part.value),
                )
            )
        elif part.type == "tool_call":
            blocks.append(
                anthropic_types.ToolUseBlockParam(
                    type="tool_use",
                    id=part.id,
                    name=part.name,
                    input=json.loads(part.args),
                )
            )
        else:
            raise NotImplementedError(f"Content type {part.type} not supported")

    return blocks


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
    else:
        raise NotImplementedError(
            f"Support for content type `{content.type}` is not yet implemented."
        )


def _encode_messages(
    messages: Sequence[UserMessage | AssistantMessage],
) -> Sequence[anthropic_types.MessageParam]:
    """Convert user or assistant `Message`s to Anthropic `MessageParam` format.

    Args:
        messages: A Sequence containing `UserMessage`s or `AssistantMessage`s

    Returns:
        A Sequence of converted Anthropic `MessageParam`
    """

    return [
        {"role": message.role, "content": _encode_content(message.content)}
        for message in messages
    ]


@lru_cache(maxsize=128)
def _convert_tool_to_tool_param(tool: Tool) -> anthropic_types.ToolParam:
    """Convert a single Mirascope tool to Anthropic tool format with caching."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    return anthropic_types.ToolParam(
        name=tool.name,
        description=tool.description,
        input_schema=schema_dict,
    )


def prepare_anthropic_request(
    messages: Sequence[Message],
    tools: Sequence[Tool] | None = None,
) -> tuple[
    Sequence[anthropic_types.MessageParam],
    str | NotGiven,
    Sequence[anthropic_types.ToolParam] | NotGiven,
]:
    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    tool_params = (
        [_convert_tool_to_tool_param(tool) for tool in tools] if tools else NotGiven()
    )

    return (
        _encode_messages(remaining_messages),
        system_message_content or NotGiven(),
        tool_params,
    )


def decode_response(
    response: anthropic_types.Message,
) -> tuple[AssistantMessage, FinishReason | None]:
    """Convert Anthropic message to mirascope AssistantMessage."""
    assistant_message = assistant(
        content=[_decode_assistant_content(part) for part in response.content]
    )
    finish_reason = (
        ANTHROPIC_FINISH_REASON_MAP.get(response.stop_reason, FinishReason.UNKNOWN)
        if response.stop_reason
        else None
    )
    return assistant_message, finish_reason


def convert_anthropic_stream_to_chunk_iterator(
    anthropic_stream_manager: MessageStreamManager,
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an Anthropic MessageStreamManager"""
    current_block_type: str | None = None

    with anthropic_stream_manager as stream:
        for event in stream._raw_stream:
            if event.type == "content_block_start":
                content_block = event.content_block
                current_block_type = content_block.type

                if content_block.type == "text":
                    yield TextStartChunk(type="text_start_chunk"), event
                else:
                    raise NotImplementedError

            elif event.type == "content_block_delta":
                delta = event.delta
                if delta.type == "text_delta":
                    yield TextChunk(type="text_chunk", delta=delta.text), event
                else:
                    raise NotImplementedError

            elif event.type == "content_block_stop":
                if current_block_type == "text":
                    yield TextEndChunk(type="text_end_chunk"), event
                else:
                    raise NotImplementedError

                current_block_type = None

            elif event.type == "message_delta":
                if event.delta.stop_reason:
                    finish_reason = ANTHROPIC_FINISH_REASON_MAP.get(
                        event.delta.stop_reason, FinishReason.UNKNOWN
                    )
                    yield FinishReasonChunk(finish_reason=finish_reason), event
