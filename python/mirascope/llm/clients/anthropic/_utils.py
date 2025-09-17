"""Anthropic message types and conversion utilities."""

import json
from collections.abc import Sequence
from functools import lru_cache
from typing import TypedDict

from anthropic import NotGiven, types as anthropic_types
from anthropic.lib.streaming import AsyncMessageStreamManager, MessageStreamManager

from ...content import (
    AssistantContentPart,
    ContentPart,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    ToolCall,
    ToolCallChunk,
    ToolCallEndChunk,
    ToolCallStartChunk,
)
from ...exceptions import FormattingModeNotSupportedError
from ...formatting import (
    FormatInfo,
    FormatT,
    _utils as _formatting_utils,
)
from ...messages import AssistantMessage, Message, UserMessage, assistant
from ...responses import (
    AsyncChunkIterator,
    ChunkIterator,
    FinishReason,
    FinishReasonChunk,
    RawChunk,
)
from ...tools import (
    FORMAT_TOOL_NAME,
    ToolSchema,
)
from ..base import _utils as _base_utils
from .model_ids import AnthropicModelId
from .params import AnthropicParams

ANTHROPIC_FINISH_REASON_MAP = {
    "end_turn": FinishReason.END_TURN,
    "max_tokens": FinishReason.MAX_TOKENS,
    "stop_sequence": FinishReason.STOP,
    "tool_use": FinishReason.TOOL_USE,
    "refusal": FinishReason.REFUSAL,
}


class MessageCreateKwargs(TypedDict, total=False):
    """Kwargs for Anthropic Message.create method."""

    model: str
    max_tokens: int
    messages: Sequence[anthropic_types.MessageParam]
    system: str | NotGiven
    tools: Sequence[anthropic_types.ToolParam] | NotGiven
    tool_choice: anthropic_types.ToolChoiceParam | NotGiven


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
def _convert_tool_to_tool_param(tool: ToolSchema) -> anthropic_types.ToolParam:
    """Convert a single Mirascope tool to Anthropic tool format with caching."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    return anthropic_types.ToolParam(
        name=tool.name,
        description=tool.description,
        input_schema=schema_dict,
    )


def prepare_anthropic_request(
    model_id: AnthropicModelId,
    messages: Sequence[Message],
    tools: Sequence[ToolSchema] | None = None,
    format: type[FormatT] | None = None,
    params: AnthropicParams | None = None,
) -> tuple[Sequence[Message], MessageCreateKwargs]:
    if params:
        raise NotImplementedError("param use not yet supported")

    kwargs: MessageCreateKwargs = {
        "model": model_id,
        "max_tokens": 1024,
    }

    anthropic_tools: list[anthropic_types.ToolParam] | NotGiven = (
        [_convert_tool_to_tool_param(tool) for tool in tools] if tools else []
    )

    if format:
        resolved_format = _formatting_utils.resolve_formattable(
            format,
            model_supports_strict_mode=False,
            model_has_native_json_support=False,
        )
        if resolved_format.mode == "strict":
            raise FormattingModeNotSupportedError(
                formatting_mode="strict", provider="anthropic", model_id=model_id
            )
        elif resolved_format.mode == "tool":
            anthropic_tools.append(create_format_tool_param(resolved_format.info))
            if tools:
                kwargs["tool_choice"] = {"type": "any"}
            else:
                kwargs["tool_choice"] = {
                    "type": "tool",
                    "name": FORMAT_TOOL_NAME,
                    "disable_parallel_tool_use": True,
                }

        if resolved_format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, resolved_format.formatting_instructions
            )

    if anthropic_tools:
        kwargs["tools"] = anthropic_tools

    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    kwargs["messages"] = _encode_messages(remaining_messages)
    if system_message_content:
        kwargs["system"] = system_message_content

    return messages, kwargs


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


class _AnthropicChunkProcessor:
    """Processes Anthropic stream events and maintains state across events."""

    def __init__(self) -> None:
        self.current_block_type: str | None = None

    def process_event(
        self, event: anthropic_types.RawMessageStreamEvent
    ) -> ChunkIterator:
        """Process a single Anthropic event and yield the appropriate content chunks."""
        yield RawChunk(raw=event)

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
            else:
                raise NotImplementedError

        elif event.type == "content_block_delta":
            delta = event.delta
            if delta.type == "text_delta":
                yield TextChunk(delta=delta.text)
            elif delta.type == "input_json_delta":
                yield ToolCallChunk(delta=delta.partial_json)
            else:
                raise NotImplementedError

        elif event.type == "content_block_stop":
            if self.current_block_type == "text":
                yield TextEndChunk()
            elif self.current_block_type == "tool_use":
                yield ToolCallEndChunk()
            else:
                raise NotImplementedError

            self.current_block_type = None

        elif event.type == "message_delta":
            if event.delta.stop_reason:
                finish_reason = ANTHROPIC_FINISH_REASON_MAP.get(
                    event.delta.stop_reason, FinishReason.UNKNOWN
                )
                yield FinishReasonChunk(finish_reason=finish_reason)


def convert_anthropic_stream_to_chunk_iterator(
    anthropic_stream_manager: MessageStreamManager,
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an Anthropic MessageStreamManager"""
    processor = _AnthropicChunkProcessor()
    with anthropic_stream_manager as stream:
        for event in stream._raw_stream:
            yield from processor.process_event(event)


async def convert_anthropic_stream_to_async_chunk_iterator(
    anthropic_stream_manager: AsyncMessageStreamManager,
) -> AsyncChunkIterator:
    """Returns an AsyncChunkIterator converted from an Anthropic MessageStreamManager"""
    processor = _AnthropicChunkProcessor()
    async with anthropic_stream_manager as stream:
        async for event in stream._raw_stream:
            for item in processor.process_event(event):
                yield item


def create_format_tool_param(
    format_info: FormatInfo,
) -> anthropic_types.ToolParam:
    """Create Anthropic ToolParam for format parsing from a Mirascope FormatInfo.

    Args:
        format_info: The FormatInfo instance containing schema and metadata

    Returns:
        Anthropic ToolParam for the format tool
    """
    schema_dict = format_info.schema.copy()
    schema_dict["type"] = "object"

    if "properties" in schema_dict and isinstance(schema_dict["properties"], dict):
        schema_dict["required"] = list(schema_dict["properties"].keys())

    description = f"Use this tool to extract data in {format_info.name} format for a final response."
    if format_info.description:
        description += "\n" + format_info.description

    return anthropic_types.ToolParam(
        name=FORMAT_TOOL_NAME,
        description=description,
        input_schema=schema_dict,
    )
