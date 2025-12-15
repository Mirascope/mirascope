"""Together AI response decoding.

Together uses an OpenAI-compatible Chat Completions response schema. This module
mirrors the OpenAI completions decode logic while targeting Together's types.

Note: Together's streaming schema (per SDK) only includes text deltas, so we
currently decode streaming tool calls only for non-streaming responses.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any, Literal

from together.types.chat_completions import (
    ChatCompletionChunk,
    ChatCompletionMessage,
    ChatCompletionResponse,
)

from ....content import (
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
from ....messages import AssistantMessage
from ....responses import (
    AsyncChunkIterator,
    ChunkIterator,
    FinishReason,
    FinishReasonChunk,
    RawStreamEventChunk,
)
from ..model_id import TogetherModelId, model_name

TOGETHER_FINISH_REASON_MAP: dict[str, FinishReason] = {
    "length": FinishReason.MAX_TOKENS,
    "content_filter": FinishReason.REFUSAL,
}


def _extract_text_from_message(message: ChatCompletionMessage) -> str | None:
    content = message.content
    if isinstance(content, str):
        return content or None
    if isinstance(
        content, list
    ):  # pragma: no cover - Together API never returns list content
        parts = [part.text or "" for part in content if part.type.value == "text"]
        text = "".join(parts)
        return text or None
    return None


def decode_response(
    response: ChatCompletionResponse,
    model_id: TogetherModelId,
) -> tuple[AssistantMessage, FinishReason | None]:
    """Convert Together ChatCompletionResponse to mirascope AssistantMessage."""
    if not response.choices:
        raise RuntimeError("Together response missing choices.")  # pragma: no cover

    choice = response.choices[0]
    if not choice.message:
        raise RuntimeError("Together response missing message.")  # pragma: no cover

    message = choice.message

    parts: list[AssistantContentPart] = []
    if (text := _extract_text_from_message(message)) is not None:
        parts.append(Text(text=text))

    if message.tool_calls:
        for tool_call in message.tool_calls:
            if not tool_call.function or not tool_call.function.name:
                continue  # pragma: no cover
            parts.append(
                ToolCall(
                    id=tool_call.id or "",
                    name=tool_call.function.name,
                    args=tool_call.function.arguments or "",
                )
            )

    finish_reason: FinishReason | None = None
    if choice.finish_reason is not None:
        finish_reason = TOGETHER_FINISH_REASON_MAP.get(choice.finish_reason.value)

    assistant_message = AssistantMessage(
        content=parts,
        provider_id="together",
        model_id=model_id,
        provider_model_name=model_name(model_id),
        raw_message=message.model_dump(mode="json", exclude_none=True),
    )

    return assistant_message, finish_reason


class _TogetherChunkProcessor:
    """Processes Together chat completion chunks and maintains state across chunks."""

    def __init__(self) -> None:
        self.current_content_type: Literal["text", "tool_call"] | None = None
        self.current_tool_index: int | None = None

    def process_chunk(self, chunk: ChatCompletionChunk) -> ChunkIterator:
        yield RawStreamEventChunk(raw_stream_event=chunk)

        if not chunk.choices:
            return  # pragma: no cover
        choice = chunk.choices[0]
        if not choice.delta:
            return  # pragma: no cover

        delta = choice.delta
        delta_content = delta.content
        if delta_content is not None and delta_content != "":
            if self.current_content_type is None:
                yield TextStartChunk()
                self.current_content_type = "text"
            yield TextChunk(delta=delta_content)

        # Together SDK's DeltaContent doesn't define tool_calls in its type (only has
        # `content: str | None`), but the API returns it. Since the SDK's BaseModel has
        # `extra="allow"`, Pydantic stores tool_calls as an extra field containing raw
        # dicts (not typed ToolCalls objects).
        tool_calls: list[dict[str, Any]] | None = getattr(delta, "tool_calls", None)
        if tool_calls:
            if self.current_content_type == "text":
                yield TextEndChunk()  # pragma: no cover
            self.current_content_type = "tool_call"

            for tc_dict in tool_calls:
                index: int = tc_dict["index"]
                func: dict[str, Any] | None = tc_dict.get("function")
                tool_id: str | None = tc_dict.get("id")
                func_name: str | None = func.get("name") if func else None
                func_args: str | None = func.get("arguments") if func else None

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
                    if not func or not func_name:
                        raise RuntimeError(
                            f"Missing name for tool call at index {index}"
                        )  # pragma: no cover

                    self.current_tool_index = index
                    if not tool_id:
                        raise RuntimeError(
                            f"Missing id for tool call at index {index}"
                        )  # pragma: no cover

                    yield ToolCallStartChunk(
                        id=tool_id,
                        name=func_name,
                    )

                if func and func_args:
                    yield ToolCallChunk(delta=func_args)

        if choice.finish_reason is not None:
            if self.current_content_type == "text":
                yield TextEndChunk()
            elif self.current_content_type == "tool_call":
                yield ToolCallEndChunk()
            self.current_content_type = None
            finish_reason = TOGETHER_FINISH_REASON_MAP.get(choice.finish_reason.value)
            if finish_reason is not None:
                yield FinishReasonChunk(finish_reason=finish_reason)


def decode_stream(
    together_stream: Iterator[ChatCompletionChunk],
) -> ChunkIterator:
    """Convert Together stream iterator to Mirascope ChunkIterator."""
    processor = _TogetherChunkProcessor()
    for chunk in together_stream:
        yield from processor.process_chunk(chunk)


async def decode_async_stream(  # pragma: no cover
    together_stream: AsyncIterator[ChatCompletionChunk],
) -> AsyncChunkIterator:
    """Convert Together async stream to Mirascope AsyncChunkIterator."""
    processor = _TogetherChunkProcessor()
    async for chunk in together_stream:
        for item in processor.process_chunk(chunk):
            yield item
