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
    RawStreamEventChunk,
)
from ..model_ids import GoogleModelId
from .encode import UNKNOWN_TOOL_ID

GOOGLE_FINISH_REASON_MAP = {
    "MAX_TOKENS": FinishReason.MAX_TOKENS,
    "SAFETY": FinishReason.REFUSAL,
    "RECITATION": FinishReason.REFUSAL,
    "BLOCKLIST": FinishReason.REFUSAL,
    "PROHIBITED_CONTENT": FinishReason.REFUSAL,
    "SPII": FinishReason.REFUSAL,
}


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
    content_parts = []
    if candidate.content and candidate.content.parts:
        for part in candidate.content.parts:
            decoded_part = _decode_content_part(part)
            if decoded_part:
                content_parts.append(decoded_part)
    return content_parts


def decode_response(
    response: genai_types.GenerateContentResponse, model_id: GoogleModelId
) -> tuple[AssistantMessage, FinishReason | None]:
    """Returns an `AssistantMessage` and `FinishReason` extracted from a `GenerateContentResponse`"""
    content: Sequence[AssistantContentPart] = []
    raw_content = []
    finish_reason: FinishReason | None = None

    if response.candidates and (candidate := response.candidates[0]):
        content = _decode_candidate_content(candidate)
        if candidate_content := candidate.content:
            raw_content = [part.model_dump() for part in candidate_content.parts or []]
        if candidate.finish_reason:
            finish_reason = GOOGLE_FINISH_REASON_MAP.get(candidate.finish_reason)

    assistant_message = AssistantMessage(
        content=content,
        provider="google",
        model_id=model_id,
        raw_content=raw_content,
    )

    return assistant_message, finish_reason


class _GoogleChunkProcessor:
    """Processes Google stream chunks and maintains state across chunks."""

    def __init__(self) -> None:
        self.current_content_type: Literal["text", "tool_call", "thought"] | None = None

    def process_chunk(
        self, chunk: genai_types.GenerateContentResponse
    ) -> ChunkIterator:
        """Process a single Google chunk and yield the appropriate content chunks."""
        yield RawStreamEventChunk(raw_stream_event=chunk)

        candidate = chunk.candidates[0] if chunk.candidates else None
        if not candidate or not candidate.content or not candidate.content.parts:
            return  # pragma: no cover

        for part in candidate.content.parts:
            if self.current_content_type == "thought" and not part.thought:
                yield ThoughtEndChunk()
                self.current_content_type = None
            elif self.current_content_type == "text" and not part.text:
                yield TextEndChunk()  # pragma: no cover
                self.current_content_type = None  # pragma: no cover
            elif self.current_content_type == "tool_call" and not part.function_call:
                # In testing, Gemini never emits tool calls and text in the same message
                # (even when specifically asked in system and user prompt), so
                # the following code is uncovered but included for completeness
                yield ToolCallEndChunk()  # pragma: no cover
                self.current_content_type = None  # pragma: no cover

            if part.thought:
                if self.current_content_type is None:
                    yield ThoughtStartChunk()
                    self.current_content_type = "thought"
                elif self.current_content_type != "thought":
                    raise RuntimeError(
                        "Received thought when not processing thought"
                    )  # pragma: no cover
                if not part.text:
                    raise ValueError(
                        "Inside thought part with no text content"
                    )  # pragma: no cover
                yield ThoughtChunk(delta=part.text)

            elif part.text:
                if self.current_content_type is None:
                    yield TextStartChunk()
                    self.current_content_type = "text"
                elif self.current_content_type != "text":
                    raise RuntimeError(
                        "Received text part when not processing text"
                    )  # pragma: no cover

                yield TextChunk(delta=part.text)

            elif function_call := part.function_call:
                if not function_call.name:
                    raise RuntimeError(
                        "Required name missing on Google function call"
                    )  # pragma: no cover

                yield ToolCallStartChunk(
                    id=function_call.id or UNKNOWN_TOOL_ID,
                    name=function_call.name,
                )

                yield ToolCallChunk(
                    delta=json.dumps(function_call.args)
                    if function_call.args
                    else "{}",
                )
                yield ToolCallEndChunk()

        if candidate.finish_reason:
            if self.current_content_type == "text":
                yield TextEndChunk()
            elif self.current_content_type == "thought":
                yield ThoughtEndChunk()  # pragma: no cover
            elif self.current_content_type is not None:
                raise NotImplementedError

            self.current_content_type = None

            finish_reason = GOOGLE_FINISH_REASON_MAP.get(candidate.finish_reason)
            if finish_reason is not None:
                yield FinishReasonChunk(finish_reason=finish_reason)


def decode_stream(
    google_stream: Iterator[genai_types.GenerateContentResponse],
) -> ChunkIterator:
    """Returns a ChunkIterator converted from a Google stream."""
    processor = _GoogleChunkProcessor()
    for chunk in google_stream:
        yield from processor.process_chunk(chunk)


async def decode_async_stream(
    google_stream: AsyncIterator[genai_types.GenerateContentResponse],
) -> AsyncChunkIterator:
    """Returns an AsyncChunkIterator converted from a Google async stream."""
    processor = _GoogleChunkProcessor()
    async for chunk in google_stream:
        for item in processor.process_chunk(chunk):
            yield item
