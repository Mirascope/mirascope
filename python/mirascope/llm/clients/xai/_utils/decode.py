"""Message decoding utilities for xAI SDK."""

from collections.abc import AsyncIterator, Iterator, Sequence
from dataclasses import asdict
from typing import Protocol, TypedDict

from xai_sdk import chat as xai_chat
from xai_sdk.proto import sample_pb2

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
)
from ..model_ids import GrokModelId


class ToolCallFunction(Protocol):
    """Protocol for tool call function structure."""

    @property
    def name(self) -> str: ...

    @property
    def arguments(self) -> str: ...


class XAIToolCall(Protocol):
    """Protocol for xAI SDK ToolCall structure."""

    @property
    def id(self) -> str: ...

    @property
    def function(self) -> ToolCallFunction: ...


class ToolCallData(TypedDict):
    """Type for accumulated tool call data."""

    name: str
    args: str


def _build_tool_calls_raw_message(
    tool_calls_data: dict[str, ToolCallData] | Sequence[XAIToolCall],
) -> list[dict[str, dict[str, str] | str]]:
    """Build raw_message tool_calls structure from tool calls data."""
    if isinstance(tool_calls_data, dict):
        return [
            {
                "id": tc_id,
                "function": {
                    "name": tc_data["name"],
                    "arguments": tc_data["args"],
                },
            }
            for tc_id, tc_data in tool_calls_data.items()
        ]
    else:
        return [
            {
                "id": tc.id,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in tool_calls_data
        ]


def _finalize_stream_content(
    accumulated_content: list[AssistantContentPart],
    current_text: str,
    current_thought: str,
    current_tool_calls: dict[str, ToolCallData],
    finish_reason: FinishReason | None,
) -> Iterator[
    ThoughtEndChunk
    | TextEndChunk
    | ToolCallEndChunk
    | FinishReasonChunk
    | RawMessageChunk
]:
    """Finalize accumulated content and yield end chunks."""
    if current_thought:
        yield ThoughtEndChunk()
        accumulated_content.append(Thought(thought=current_thought))

    if current_text:
        yield TextEndChunk()
        accumulated_content.append(Text(text=current_text))

    for tc_id, tc_data in current_tool_calls.items():
        yield ToolCallEndChunk(id=tc_id)
        accumulated_content.append(
            ToolCall(id=tc_id, name=tc_data["name"], args=tc_data["args"])
        )

    if finish_reason:
        yield FinishReasonChunk(finish_reason=finish_reason)

    raw_message: dict = {
        "content": [asdict(part) for part in accumulated_content],
    }
    if current_tool_calls:
        raw_message["tool_calls"] = _build_tool_calls_raw_message(current_tool_calls)

    yield RawMessageChunk(raw_message=raw_message)


async def _finalize_async_stream_content(
    accumulated_content: list[AssistantContentPart],
    current_text: str,
    current_thought: str,
    current_tool_calls: dict[str, ToolCallData],
    finish_reason: FinishReason | None,
) -> AsyncIterator[
    ThoughtEndChunk
    | TextEndChunk
    | ToolCallEndChunk
    | FinishReasonChunk
    | RawMessageChunk
]:
    """Finalize accumulated content and yield end chunks (async version)."""
    if current_thought:
        yield ThoughtEndChunk()
        accumulated_content.append(Thought(thought=current_thought))

    if current_text:
        yield TextEndChunk()
        accumulated_content.append(Text(text=current_text))

    for tc_id, tc_data in current_tool_calls.items():
        yield ToolCallEndChunk(id=tc_id)
        accumulated_content.append(
            ToolCall(id=tc_id, name=tc_data["name"], args=tc_data["args"])
        )

    if finish_reason:
        yield FinishReasonChunk(finish_reason=finish_reason)

    raw_message: dict = {
        "content": [asdict(part) for part in accumulated_content],
    }
    if current_tool_calls:
        raw_message["tool_calls"] = _build_tool_calls_raw_message(current_tool_calls)

    yield RawMessageChunk(raw_message=raw_message)


def decode_response(
    response: xai_chat.Response, model_id: GrokModelId
) -> tuple[AssistantMessage, FinishReason | None]:
    """Convert an xAI SDK response to Mirascope AssistantMessage."""
    content_parts: list[AssistantContentPart] = []

    if response.reasoning_content:
        content_parts.append(Thought(thought=response.reasoning_content))

    if response.content:
        content_parts.append(Text(text=response.content))

    if response.tool_calls:
        for tool_call in response.tool_calls:
            content_parts.append(
                ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    args=tool_call.function.arguments,
                )
            )

    finish_reason: FinishReason | None = None
    if response.finish_reason in (
        sample_pb2.REASON_MAX_LEN,
        sample_pb2.REASON_MAX_CONTEXT,
    ):
        finish_reason = FinishReason.MAX_TOKENS

    raw_message: dict = {
        "content": [asdict(part) for part in content_parts],
    }
    if response.tool_calls:
        raw_message["tool_calls"] = _build_tool_calls_raw_message(response.tool_calls)

    assistant_message = AssistantMessage(
        content=content_parts,
        provider="xai",
        model_id=model_id,
        raw_message=raw_message,
    )

    return assistant_message, finish_reason


def decode_stream(
    xai_stream: Iterator[tuple[xai_chat.Response, xai_chat.Chunk]],
    model_id: GrokModelId,
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an xAI SDK stream."""
    accumulated_content: list[AssistantContentPart] = []
    current_text = ""
    current_thought = ""
    current_tool_calls: dict[str, ToolCallData] = {}
    finish_reason: FinishReason | None = None

    for _response, chunk in xai_stream:
        yield RawStreamEventChunk(raw_stream_event=chunk)

        if chunk.reasoning_content:
            if not current_thought:
                yield ThoughtStartChunk()
            yield ThoughtChunk(delta=chunk.reasoning_content)
            current_thought += chunk.reasoning_content

        if chunk.content:
            if not current_text:
                yield TextStartChunk()
            yield TextChunk(delta=chunk.content)
            current_text += chunk.content

        if chunk.tool_calls:
            for tc_delta in chunk.tool_calls:
                tc_id = tc_delta.id
                if not tc_id:
                    continue
                if tc_id not in current_tool_calls:
                    tc_name = tc_delta.function.name if tc_delta.function else ""
                    current_tool_calls[tc_id] = {
                        "name": tc_name,
                        "args": "",
                    }
                    yield ToolCallStartChunk(id=tc_id, name=tc_name)

                if tc_delta.function and tc_delta.function.arguments:
                    args_delta = tc_delta.function.arguments
                    current_tool_calls[tc_id]["args"] += args_delta
                    yield ToolCallChunk(id=tc_id, delta=args_delta)

        if (
            chunk.choices
            and chunk.choices[0].finish_reason
            and (
                chunk.choices[0].finish_reason == sample_pb2.REASON_MAX_LEN
                or chunk.choices[0].finish_reason == sample_pb2.REASON_MAX_CONTEXT
            )
        ):
            finish_reason = FinishReason.MAX_TOKENS

    yield from _finalize_stream_content(
        accumulated_content,
        current_text,
        current_thought,
        current_tool_calls,
        finish_reason,
    )


async def decode_async_stream(
    xai_stream: AsyncIterator[tuple[xai_chat.Response, xai_chat.Chunk]],
    model_id: GrokModelId,
) -> AsyncChunkIterator:
    """Returns an AsyncChunkIterator converted from an xAI SDK async stream."""
    accumulated_content: list[AssistantContentPart] = []
    current_text = ""
    current_thought = ""
    current_tool_calls: dict[str, ToolCallData] = {}
    finish_reason: FinishReason | None = None

    async for _response, chunk in xai_stream:
        yield RawStreamEventChunk(raw_stream_event=chunk)

        if chunk.reasoning_content:
            if not current_thought:
                yield ThoughtStartChunk()
            yield ThoughtChunk(delta=chunk.reasoning_content)
            current_thought += chunk.reasoning_content

        if chunk.content:
            if not current_text:
                yield TextStartChunk()
            yield TextChunk(delta=chunk.content)
            current_text += chunk.content

        if chunk.tool_calls:
            for tc_delta in chunk.tool_calls:
                tc_id = tc_delta.id
                if not tc_id:
                    continue
                if tc_id not in current_tool_calls:
                    tc_name = tc_delta.function.name if tc_delta.function else ""
                    current_tool_calls[tc_id] = {
                        "name": tc_name,
                        "args": "",
                    }
                    yield ToolCallStartChunk(id=tc_id, name=tc_name)

                if tc_delta.function and tc_delta.function.arguments:
                    args_delta = tc_delta.function.arguments
                    current_tool_calls[tc_id]["args"] += args_delta
                    yield ToolCallChunk(id=tc_id, delta=args_delta)

        if (
            chunk.choices
            and chunk.choices[0].finish_reason
            and (
                chunk.choices[0].finish_reason == sample_pb2.REASON_MAX_LEN
                or chunk.choices[0].finish_reason == sample_pb2.REASON_MAX_CONTEXT
            )
        ):
            finish_reason = FinishReason.MAX_TOKENS

    async for chunk in _finalize_async_stream_content(
        accumulated_content,
        current_text,
        current_thought,
        current_tool_calls,
        finish_reason,
    ):
        yield chunk
