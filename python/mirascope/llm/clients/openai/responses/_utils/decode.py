"""OpenAI Responses response decoding."""

from typing import Any, Literal

from openai import AsyncStream, Stream
from openai.types import responses as openai_types
from openai.types.responses.response_stream_event import ResponseStreamEvent

from .....content import (
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
from .....messages import AssistantMessage
from .....responses import (
    AsyncChunkIterator,
    ChunkIterator,
    FinishReason,
    FinishReasonChunk,
    RawMessageChunk,
    RawStreamEventChunk,
)
from ...model_info import OpenAIModelId

INCOMPLETE_DETAILS_TO_FINISH_REASON = {
    "max_output_tokens": FinishReason.MAX_TOKENS,
    "content_filter": FinishReason.REFUSAL,
}


def get_provider_model_id(model_id: OpenAIModelId) -> str:
    """Extract the provider-specific model ID from a full model ID.

    Args:
        model_id: Full model ID (e.g. "openai/gpt-4o")

    Returns:
        Provider-specific model ID with API suffix (e.g. "gpt-4o:responses")
    """
    model_name = model_id.removeprefix("openai/").removesuffix(":responses")
    return f"{model_name}:responses"


def _serialize_output_item(
    item: openai_types.ResponseOutputItem,
) -> dict[str, Any]:
    """Returns the item serialized as a dictionary."""
    return {key: value for key, value in item.model_dump().items() if value is not None}


def decode_response(
    response: openai_types.Response,
    model_id: OpenAIModelId,
) -> tuple[AssistantMessage, FinishReason | None]:
    """Convert OpenAI Responses Response to mirascope AssistantMessage."""
    parts: list[AssistantContentPart] = []
    finish_reason: FinishReason | None = None
    refused = False

    for output_item in response.output:
        if output_item.type == "message":
            for content in output_item.content:
                if content.type == "output_text":
                    parts.append(Text(text=content.text))
                elif content.type == "refusal":
                    parts.append(Text(text=content.refusal))
                    refused = True
        elif output_item.type == "function_call":
            parts.append(
                ToolCall(
                    id=output_item.call_id,
                    name=output_item.name,
                    args=output_item.arguments,
                )
            )
        elif output_item.type == "reasoning":
            for summary_part in output_item.summary:
                if summary_part.type == "summary_text":
                    parts.append(Thought(thought=summary_part.text))
            if output_item.content:  # pragma: no cover
                # TODO: Add test case covering this
                # (Likely their open-source models output reasoning_text rather than summaries)
                for reasoning_content in output_item.content:
                    if reasoning_content.type == "reasoning_text":
                        parts.append(Thought(thought=reasoning_content.text))

        else:
            raise NotImplementedError(f"Unsupported output item: {output_item.type}")

    if refused:
        finish_reason = FinishReason.REFUSAL
    elif details := response.incomplete_details:
        finish_reason = INCOMPLETE_DETAILS_TO_FINISH_REASON.get(details.reason or "")

    assistant_message = AssistantMessage(
        content=parts,
        provider="openai",
        model_id=model_id,
        provider_model_id=get_provider_model_id(model_id),
        raw_message=[
            _serialize_output_item(output_item) for output_item in response.output
        ],
    )

    return assistant_message, finish_reason


class _OpenAIResponsesChunkProcessor:
    """Processes OpenAI Responses streaming events and maintains state across chunks."""

    def __init__(self) -> None:
        self.current_content_type: Literal["text", "tool_call", "thought"] | None = None
        self.refusal_encountered = False

    def process_chunk(self, event: ResponseStreamEvent) -> ChunkIterator:
        """Process a single OpenAI Responses stream event and yield the appropriate content chunks."""
        yield RawStreamEventChunk(raw_stream_event=event)

        if hasattr(event, "type"):
            if event.type == "response.output_text.delta":
                if not self.current_content_type:
                    yield TextStartChunk()
                    self.current_content_type = "text"
                yield TextChunk(delta=event.delta)
            elif event.type == "response.output_text.done":
                yield TextEndChunk()
                self.current_content_type = None
            if event.type == "response.refusal.delta":
                if not self.current_content_type:
                    yield TextStartChunk()
                    self.current_content_type = "text"
                yield TextChunk(delta=event.delta)
            elif event.type == "response.refusal.done":
                yield TextEndChunk()
                self.refusal_encountered = True
                self.current_content_type = None
            elif event.type == "response.output_item.added":
                item = event.item
                if item.type == "function_call":
                    self.current_tool_call_id = item.call_id
                    self.current_tool_call_name = item.name
                    yield ToolCallStartChunk(
                        id=item.call_id,
                        name=item.name,
                    )
                    self.current_content_type = "tool_call"
            elif event.type == "response.function_call_arguments.delta":
                yield ToolCallChunk(delta=event.delta)
            elif event.type == "response.function_call_arguments.done":
                yield ToolCallEndChunk()
                self.current_content_type = None
            elif (
                event.type == "response.reasoning_text.delta"
                or event.type == "response.reasoning_summary_text.delta"
            ):
                if not self.current_content_type:
                    yield ThoughtStartChunk()
                    self.current_content_type = "thought"
                yield ThoughtChunk(delta=event.delta)
            elif (
                event.type == "response.reasoning_summary_text.done"
                or event.type == "response.reasoning_text.done"
            ):
                yield ThoughtEndChunk()
                self.current_content_type = None
            elif event.type == "response.incomplete":
                details = event.response.incomplete_details
                reason = (details and details.reason) or ""
                finish_reason = INCOMPLETE_DETAILS_TO_FINISH_REASON.get(reason)
                if finish_reason:
                    yield FinishReasonChunk(finish_reason=finish_reason)
            elif event.type == "response.completed":
                yield RawMessageChunk(
                    raw_message=[
                        _serialize_output_item(item) for item in event.response.output
                    ]
                )
                if self.refusal_encountered:
                    yield FinishReasonChunk(finish_reason=FinishReason.REFUSAL)


def decode_stream(
    openai_stream: Stream[ResponseStreamEvent],
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an OpenAI Stream[ResponseStreamEvent]"""
    processor = _OpenAIResponsesChunkProcessor()
    for event in openai_stream:
        yield from processor.process_chunk(event)


async def decode_async_stream(
    openai_stream: AsyncStream[ResponseStreamEvent],
) -> AsyncChunkIterator:
    """Returns an AsyncChunkIterator converted from an OpenAI AsyncStream[ResponseStreamEvent]"""
    processor = _OpenAIResponsesChunkProcessor()
    async for event in openai_stream:
        for item in processor.process_chunk(event):
            yield item
