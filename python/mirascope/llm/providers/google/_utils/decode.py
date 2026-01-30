"""Google response decoding."""

import json
from collections.abc import AsyncIterator, Iterator, Sequence
from typing import Literal

from google.genai import types as genai_types

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
    ProviderToolUsage,
    RawMessageChunk,
    RawStreamEventChunk,
    Usage,
    UsageDeltaChunk,
)
from ..model_id import GoogleModelId, model_name
from .encode import UNKNOWN_TOOL_ID

GOOGLE_FINISH_REASON_MAP = {
    "MAX_TOKENS": FinishReason.MAX_TOKENS,
    "SAFETY": FinishReason.REFUSAL,
    "RECITATION": FinishReason.REFUSAL,
    "BLOCKLIST": FinishReason.REFUSAL,
    "PROHIBITED_CONTENT": FinishReason.REFUSAL,
    "SPII": FinishReason.REFUSAL,
}


def _extract_tool_usage(
    candidate: genai_types.Candidate | None,
) -> list[ProviderToolUsage] | None:
    """Extract provider tool usage from Google candidate's grounding metadata."""
    if candidate is None:  # pragma: no cover
        return None

    grounding_metadata = candidate.grounding_metadata
    if grounding_metadata is None:
        return None

    tools: list[ProviderToolUsage] = []

    # Web search queries indicate grounding was used
    web_search_queries = grounding_metadata.web_search_queries
    if web_search_queries and len(web_search_queries) > 0:
        tools.append(
            ProviderToolUsage(name="web_search", call_count=len(web_search_queries))
        )

    return tools if tools else None


def _decode_usage(
    usage: genai_types.GenerateContentResponseUsageMetadata | None,
    candidate: genai_types.Candidate | None = None,
) -> Usage | None:
    """Convert Google UsageMetadata to Mirascope Usage."""
    if (
        usage is None
        or usage.prompt_token_count is None
        or usage.candidates_token_count is None
    ):  # pragma: no cover
        return None

    reasoning_tokens = usage.thoughts_token_count or 0
    output_tokens = usage.candidates_token_count + reasoning_tokens

    return Usage(
        input_tokens=usage.prompt_token_count,
        output_tokens=output_tokens,
        cache_read_tokens=usage.cached_content_token_count or 0,
        cache_write_tokens=0,
        reasoning_tokens=usage.thoughts_token_count or 0,
        provider_tool_usage=_extract_tool_usage(candidate),
        raw=usage,
    )


def _decode_content_part(part: genai_types.Part) -> AssistantContentPart | None:
    """Returns an `AssistantContentPart` (or `None`) decoded from a google `Part`"""
    if part.thought and part.text:
        return Thought(thought=part.text)
    elif part.text:
        return Text(text=part.text)
    elif part.video_metadata:
        raise NotImplementedError("Support for video metadata not implemented.")
    elif part.inline_data:
        raise NotImplementedError("Support for inline data (Blob) not implemented.")
    elif part.file_data:
        raise NotImplementedError("Support for file data (FileData) not implemented.")
    elif part.code_execution_result:
        raise NotImplementedError("Support for code execution results not implemented.")
    elif part.executable_code:
        raise NotImplementedError("Support for executable code not implemented.")
    elif function_call := part.function_call:
        id = function_call.id
        name = function_call.name
        args = function_call.args
        if not name or args is None:
            raise ValueError(
                "Google function_call does not match spec"
            )  # pragma: no cover
        return ToolCall(id=id or UNKNOWN_TOOL_ID, name=name, args=json.dumps(args))
    elif part.function_response:  # pragma: no cover
        raise NotImplementedError(
            "function_response part does not decode to AssistantContent."
        )
    elif part.thought_signature:  # pragma: no cover
        raise NotImplementedError("Support for thought signature not implemented.")
    else:  # pragma: no cover
        # Per Part docstring, this should never happen:
        # >  Exactly one field within a Part should be set, representing the specific type
        # >  of content being conveyed. Using multiple fields within the same `Part`
        # >  instance is considered invalid.
        # However, in testing, this can happen, so we will do our best to handle
        # it as empty content.
        return None


def _decode_candidate_content(
    candidate: genai_types.Candidate,
) -> Sequence[AssistantContentPart]:
    """Returns a sequence of `AssistantContentPart` decoded from a google `Candidate`"""
    content_parts: list[AssistantContentPart] = []
    if candidate.content and candidate.content.parts:
        for part in candidate.content.parts:
            decoded_part = _decode_content_part(part)
            if decoded_part:
                content_parts.append(decoded_part)
    return content_parts


def decode_response(
    response: genai_types.GenerateContentResponse,
    model_id: GoogleModelId,
    *,
    include_thoughts: bool,
) -> tuple[AssistantMessage, FinishReason | None, Usage | None]:
    """Returns an `AssistantMessage`, `FinishReason`, and `Usage` extracted from a `GenerateContentResponse`"""
    content: Sequence[AssistantContentPart] = []
    candidate_content: genai_types.Content | None = None
    finish_reason: FinishReason | None = None

    if response.candidates and (candidate := response.candidates[0]):
        content = _decode_candidate_content(candidate)
        if not include_thoughts:
            content = [part for part in content if part.type != "thought"]
        candidate_content = candidate.content
        if candidate.finish_reason:
            finish_reason = GOOGLE_FINISH_REASON_MAP.get(candidate.finish_reason)

    candidate_content = candidate_content or genai_types.Content()

    assistant_message = AssistantMessage(
        content=content,
        provider_id="google",
        model_id=model_id,
        provider_model_name=model_name(model_id),
        raw_message=candidate_content.model_dump(),
    )

    candidate = response.candidates[0] if response.candidates else None
    usage = _decode_usage(response.usage_metadata, candidate)
    return assistant_message, finish_reason, usage


class _GoogleChunkProcessor:
    """Processes Google stream chunks and maintains state across chunks."""

    def __init__(self, *, include_thoughts: bool) -> None:
        self.current_content_type: Literal["text", "tool_call", "thought"] | None = None
        self.accumulated_parts: list[genai_types.Part] = []
        self.reconstructed_content = genai_types.Content(parts=[])
        # Track previous cumulative usage to compute deltas
        self.prev_usage = Usage()
        self.include_thoughts = include_thoughts
        # Track web search queries count from grounding metadata
        self.web_search_query_count = 0

    def process_chunk(
        self, chunk: genai_types.GenerateContentResponse
    ) -> ChunkIterator:
        """Process a single Google chunk and yield the appropriate content chunks."""
        yield RawStreamEventChunk(raw_stream_event=chunk)

        candidate = chunk.candidates[0] if chunk.candidates else None
        if not candidate or not candidate.content or not candidate.content.parts:
            return  # pragma: no cover

        for part in candidate.content.parts:
            self.accumulated_parts.append(part)
            if self.current_content_type == "thought" and not part.thought:
                if self.include_thoughts:
                    yield ThoughtEndChunk()
                self.current_content_type = None
            elif (
                self.current_content_type == "text" and not part.text
            ):  # pragma: no cover
                yield TextEndChunk()
                self.current_content_type = None
            elif (
                self.current_content_type == "tool_call" and not part.function_call
            ):  # pragma: no cover
                # In testing, Gemini never emits tool calls and text in the same message
                # (even when specifically asked in system and user prompt), so
                # the following code is uncovered but included for completeness
                yield ToolCallEndChunk(id=UNKNOWN_TOOL_ID)
                self.current_content_type = None

            if part.thought:
                if self.current_content_type is None:
                    if self.include_thoughts:
                        yield ThoughtStartChunk()
                    self.current_content_type = "thought"
                if not part.text:
                    raise ValueError(
                        "Inside thought part with no text content"
                    )  # pragma: no cover
                if self.include_thoughts:
                    yield ThoughtChunk(delta=part.text)

            elif part.text:
                if self.current_content_type is None:
                    yield TextStartChunk()
                    self.current_content_type = "text"

                yield TextChunk(delta=part.text)

            elif function_call := part.function_call:
                if not function_call.name:
                    raise RuntimeError(
                        "Required name missing on Google function call"
                    )  # pragma: no cover

                tool_id = function_call.id or UNKNOWN_TOOL_ID
                self.current_content_type = "tool_call"

                yield ToolCallStartChunk(
                    id=tool_id,
                    name=function_call.name,
                )

                yield ToolCallChunk(
                    id=tool_id,
                    delta=json.dumps(function_call.args)
                    if function_call.args
                    else "{}",
                )
                yield ToolCallEndChunk(id=tool_id)
                self.current_content_type = None

        # Track web search queries from grounding metadata
        if (
            candidate.grounding_metadata
            and candidate.grounding_metadata.web_search_queries
        ):
            self.web_search_query_count = len(
                candidate.grounding_metadata.web_search_queries
            )

        if candidate.finish_reason:
            if self.current_content_type == "text":
                yield TextEndChunk()
            elif self.current_content_type == "thought":
                if self.include_thoughts:  # pragma: no cover
                    yield ThoughtEndChunk()
            elif self.current_content_type is not None:
                raise NotImplementedError

            self.current_content_type = None

            finish_reason = GOOGLE_FINISH_REASON_MAP.get(candidate.finish_reason)
            if finish_reason is not None:
                yield FinishReasonChunk(finish_reason=finish_reason)

        # Emit usage delta if usage metadata is present
        if chunk.usage_metadata:
            usage_metadata = chunk.usage_metadata
            current_input = usage_metadata.prompt_token_count or 0
            current_output = usage_metadata.candidates_token_count or 0
            current_cache_read = usage_metadata.cached_content_token_count or 0
            current_reasoning = usage_metadata.thoughts_token_count or 0

            # Include provider_tool_usage on the final usage chunk (when finish_reason is present)
            provider_tool_usage = (
                [
                    ProviderToolUsage(
                        name="web_search", call_count=self.web_search_query_count
                    )
                ]
                if candidate.finish_reason and self.web_search_query_count > 0
                else None
            )

            yield UsageDeltaChunk(
                input_tokens=current_input - self.prev_usage.input_tokens,
                output_tokens=current_output - self.prev_usage.output_tokens,
                cache_read_tokens=current_cache_read
                - self.prev_usage.cache_read_tokens,
                cache_write_tokens=0,
                reasoning_tokens=current_reasoning - self.prev_usage.reasoning_tokens,
                provider_tool_usage=provider_tool_usage,
            )

            # Update previous usage
            self.prev_usage.input_tokens = current_input
            self.prev_usage.output_tokens = current_output
            self.prev_usage.cache_read_tokens = current_cache_read
            self.prev_usage.reasoning_tokens = current_reasoning

    def raw_message_chunk(self) -> RawMessageChunk:
        content = genai_types.Content(role="model", parts=self.accumulated_parts)
        return RawMessageChunk(raw_message=content.model_dump())


def decode_stream(
    google_stream: Iterator[genai_types.GenerateContentResponse],
    *,
    include_thoughts: bool,
) -> ChunkIterator:
    """Returns a ChunkIterator converted from a Google stream."""
    processor = _GoogleChunkProcessor(include_thoughts=include_thoughts)
    for chunk in google_stream:
        yield from processor.process_chunk(chunk)
    yield processor.raw_message_chunk()


async def decode_async_stream(
    google_stream: AsyncIterator[genai_types.GenerateContentResponse],
    *,
    include_thoughts: bool,
) -> AsyncChunkIterator:
    """Returns an AsyncChunkIterator converted from a Google async stream."""
    processor = _GoogleChunkProcessor(include_thoughts=include_thoughts)
    async for chunk in google_stream:
        for item in processor.process_chunk(chunk):
            yield item
    yield processor.raw_message_chunk()
