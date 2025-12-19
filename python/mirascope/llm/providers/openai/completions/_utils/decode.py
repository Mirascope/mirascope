"""OpenAI completions response decoding."""

from typing import Literal

from openai import AsyncStream, Stream
from openai.types import chat as openai_types
from openai.types.completion_usage import CompletionUsage

from .....content import (
    AssistantContentPart,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    ToolCall,
    ToolCallChunk,
    ToolCallEndChunk,
    ToolCallStartChunk,
)
from .....messages import AssistantMessage
from .....responses import (
    AsyncChunkIterator,
    ChunkIterator,
    FinishReason,
    FinishReasonChunk,
    RawStreamEventChunk,
    Usage,
    UsageDeltaChunk,
)
from ...model_id import OpenAIModelId, model_name

OPENAI_FINISH_REASON_MAP = {
    "length": FinishReason.MAX_TOKENS,
    "content_filter": FinishReason.REFUSAL,
}


def _decode_usage(
    usage: CompletionUsage | None,
) -> Usage | None:
    """Convert OpenAI CompletionUsage to Mirascope Usage."""
    if usage is None:  # pragma: no cover
        return None

    return Usage(
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
        cache_read_tokens=(
            usage.prompt_tokens_details.cached_tokens
            if usage.prompt_tokens_details
            else None
        )
        or 0,
        cache_write_tokens=0,
        reasoning_tokens=(
            usage.completion_tokens_details.reasoning_tokens
            if usage.completion_tokens_details
            else None
        )
        or 0,
        raw=usage,
    )


def decode_response(
    response: openai_types.ChatCompletion,
    model_id: OpenAIModelId,
    provider_id: str,
    provider_model_name: str | None = None,
) -> tuple[AssistantMessage, FinishReason | None, Usage | None]:
    """Convert OpenAI ChatCompletion to mirascope AssistantMessage and usage."""
    choice = response.choices[0]
    message = choice.message
    refused = False

    parts: list[AssistantContentPart] = []
    if message.content:
        parts.append(Text(text=message.content))
    if message.refusal:
        parts.append(Text(text=message.refusal))
        refused = True
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.type == "custom":
                # This should never happen, because we never create "custom" tools
                # https://platform.openai.com/docs/guides/function-calling#custom-tools
                raise NotImplementedError("OpenAI custom tools are not supported.")
            parts.append(
                ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    args=tool_call.function.arguments,
                )
            )

    finish_reason = (
        FinishReason.REFUSAL
        if refused
        else OPENAI_FINISH_REASON_MAP.get(choice.finish_reason)
    )

    assistant_message = AssistantMessage(
        content=parts,
        provider_id=provider_id,
        model_id=model_id,
        provider_model_name=provider_model_name or model_name(model_id, "completions"),
        raw_message=message.model_dump(exclude_none=True),
    )

    usage = _decode_usage(response.usage)
    return assistant_message, finish_reason, usage


class _OpenAIChunkProcessor:
    """Processes OpenAI chat completion chunks and maintains state across chunks."""

    def __init__(self) -> None:
        self.current_content_type: Literal["text", "tool_call"] | None = None
        self.current_tool_index: int | None = None
        self.refusal_encountered = False

    def process_chunk(self, chunk: openai_types.ChatCompletionChunk) -> ChunkIterator:
        """Process a single OpenAI chunk and yield the appropriate content chunks."""
        yield RawStreamEventChunk(raw_stream_event=chunk)

        if chunk.usage:
            usage = chunk.usage
            yield UsageDeltaChunk(
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                cache_read_tokens=(
                    usage.prompt_tokens_details.cached_tokens
                    if usage.prompt_tokens_details
                    else None
                )
                or 0,
                cache_write_tokens=0,
                reasoning_tokens=(
                    usage.completion_tokens_details.reasoning_tokens
                    if usage.completion_tokens_details
                    else None
                )
                or 0,
            )

        choice = chunk.choices[0] if chunk.choices else None
        if not choice:
            return  # pragma: no cover

        delta = choice.delta

        content = delta.content or delta.refusal
        if delta.refusal:
            self.refusal_encountered = True
        if content is not None:
            if self.current_content_type is None:
                yield TextStartChunk()
                self.current_content_type = "text"
            yield TextChunk(delta=content)

        if delta.tool_calls:
            if self.current_content_type == "text":
                # In testing, I can't get OpenAI to emit text and tool calls in the same chunk
                # But we handle this defensively.
                yield TextEndChunk()  # pragma: no cover
            self.current_content_type = "tool_call"

            for tool_call_delta in delta.tool_calls:
                index = tool_call_delta.index

                if (
                    self.current_tool_index is not None
                    and self.current_tool_index > index
                ):
                    raise RuntimeError(
                        f"Received tool data for already-finished tool at index {index}"
                    )  # pragma: no cover

                if (
                    self.current_tool_index is not None
                    and self.current_tool_index < index
                ):
                    yield ToolCallEndChunk()
                    self.current_tool_index = None

                if self.current_tool_index is None:
                    if not tool_call_delta.function or not (
                        name := tool_call_delta.function.name
                    ):
                        raise RuntimeError(
                            f"Missing name for tool call at index {index}"
                        )  # pragma: no cover

                    self.current_tool_index = index
                    if not (tool_id := tool_call_delta.id):
                        raise RuntimeError(
                            f"Missing id for tool call at index {index}"
                        )  # pragma: no cover

                    yield ToolCallStartChunk(
                        id=tool_id,
                        name=name,
                    )

                if tool_call_delta.function and tool_call_delta.function.arguments:
                    yield ToolCallChunk(delta=tool_call_delta.function.arguments)

        if choice.finish_reason:
            if self.current_content_type == "text":
                yield TextEndChunk()
            elif self.current_content_type == "tool_call":
                yield ToolCallEndChunk()
            elif self.current_content_type is not None:  # pragma: no cover
                raise NotImplementedError()

            finish_reason = (
                FinishReason.REFUSAL
                if self.refusal_encountered
                else OPENAI_FINISH_REASON_MAP.get(choice.finish_reason)
            )
            if finish_reason is not None:
                yield FinishReasonChunk(finish_reason=finish_reason)


def decode_stream(
    openai_stream: Stream[openai_types.ChatCompletionChunk],
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an OpenAI Stream[ChatCompletionChunk]"""
    processor = _OpenAIChunkProcessor()
    for chunk in openai_stream:
        yield from processor.process_chunk(chunk)


async def decode_async_stream(
    openai_stream: AsyncStream[openai_types.ChatCompletionChunk],
) -> AsyncChunkIterator:
    """Returns an AsyncChunkIterator converted from an OpenAI AsyncStream[ChatCompletionChunk]"""
    processor = _OpenAIChunkProcessor()
    async for chunk in openai_stream:
        for item in processor.process_chunk(chunk):
            yield item
