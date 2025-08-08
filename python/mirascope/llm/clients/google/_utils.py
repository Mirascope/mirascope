"""Google message types and conversion utilities."""

from collections.abc import Iterator, Sequence
from typing import Literal

from google.genai import types as genai_types
from google.genai.types import GenerateContentConfig

from ...content import (
    AssistantContentPart,
    ContentPart,
    FinishReasonChunk,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
)
from ...messages import AssistantMessage, Message, UserMessage, assistant
from ...responses import ChunkIterator, FinishReason
from ..base import _utils as _base_utils

GOOGLE_FINISH_REASON_MAP = {  # TODO (mir-285): Audit these
    "STOP": FinishReason.END_TURN,
    "MAX_TOKENS": FinishReason.MAX_TOKENS,
    "SAFETY": FinishReason.REFUSAL,
    "RECITATION": FinishReason.REFUSAL,
    "OTHER": FinishReason.UNKNOWN,
    "BLOCKLIST": FinishReason.REFUSAL,
    "PROHIBITED_CONTENT": FinishReason.REFUSAL,
    "SPII": FinishReason.REFUSAL,
    "MALFORMED_FUNCTION_CALL": FinishReason.UNKNOWN,
}


def _encode_content(content: Sequence[ContentPart]) -> list[genai_types.PartDict]:
    """Returns a list of google `PartDicts` converted from a sequence of Mirascope `ContentPart`s"""
    result = []
    for item in content:
        if item.type == "text":
            result.append({"text": item.text})
        else:
            raise NotImplementedError(
                f"Have not implemented conversion for {item.type}"
            )
    return result


def _decode_content_part(part: genai_types.Part) -> AssistantContentPart | None:
    """Returns an `AssistantContentPart` (or `None`) decoded from a google `Part`"""
    if part.text:
        return Text(text=part.text)
    elif part.video_metadata:
        raise NotImplementedError("Support for video metadata not implemented.")
    elif part.thought:
        raise NotImplementedError("Support for thought content not implemented.")
    elif part.inline_data:
        raise NotImplementedError("Support for inline data (Blob) not implemented.")
    elif part.file_data:
        raise NotImplementedError("Support for file data (FileData) not implemented.")
    elif part.thought_signature:
        raise NotImplementedError("Support for thought signature not implemented.")
    elif part.code_execution_result:
        raise NotImplementedError("Support for code execution results not implemented.")
    elif part.executable_code:
        raise NotImplementedError("Support for executable code not implemented.")
    elif part.function_call:
        raise NotImplementedError("Support for function calls not implemented.")
    elif part.function_response:
        raise NotImplementedError("Support for function responses not implemented.")
    else:
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


def _encode_message(
    message: UserMessage | AssistantMessage,
) -> genai_types.ContentDict:
    """Returns a Google `ContentDict` converted from a Mirascope `Message`"""
    return {
        "role": "model" if message.role == "assistant" else message.role,
        "parts": _encode_content(message.content),
    }


def _encode_messages(
    messages: Sequence[UserMessage | AssistantMessage],
) -> genai_types.ContentListUnionDict:
    """Returns a `ContentListUnionDict` converted from a sequence of user or assistant `Messages`s"""
    return [_encode_message(message) for message in messages]


def prepare_google_request(
    messages: Sequence[Message],
) -> tuple[genai_types.ContentListUnionDict, GenerateContentConfig | None]:
    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    config = None
    if system_message_content:
        config = GenerateContentConfig(system_instruction=system_message_content)

    return _encode_messages(remaining_messages), config


def decode_response(
    response: genai_types.GenerateContentResponse,
) -> tuple[AssistantMessage, FinishReason | None]:
    """Returns an `AssistantMessage` and `FinishReason` extracted from a `GenerateContentResponse`"""
    if not response.candidates or not response.candidates[0].content:
        # Unclear under what circumstances this happens (if ever).
        # In testing, when generating no output at all, it creates a part with
        # no fields set.
        return assistant(content=[]), FinishReason.UNKNOWN  # pragma: no cover
    candidate = response.candidates[0]
    assistant_message = assistant(content=_decode_candidate_content(candidate))
    finish_reason = (
        GOOGLE_FINISH_REASON_MAP.get(candidate.finish_reason, FinishReason.UNKNOWN)
        if candidate.finish_reason
        else None
    )
    return assistant_message, finish_reason


def convert_google_stream_to_chunk_iterator(
    google_stream: Iterator[genai_types.GenerateContentResponse],
) -> ChunkIterator:
    current_content_type: Literal["text"] | None = None

    for chunk in google_stream:
        candidate = chunk.candidates[0] if chunk.candidates else None
        if not candidate or not candidate.content or not candidate.content.parts:
            continue  # pragma: no cover

        for part in candidate.content.parts:
            if part.thought:
                raise NotImplementedError

            elif part.text:
                if current_content_type is None:
                    yield TextStartChunk(type="text_start_chunk"), chunk
                    current_content_type = "text"
                elif current_content_type != "text":
                    raise NotImplementedError

                yield TextChunk(type="text_chunk", delta=part.text), chunk

        if candidate.finish_reason:
            if current_content_type == "text":
                yield TextEndChunk(type="text_end_chunk"), chunk
            else:
                raise NotImplementedError

            finish_reason = GOOGLE_FINISH_REASON_MAP.get(
                candidate.finish_reason, FinishReason.UNKNOWN
            )
            yield FinishReasonChunk(finish_reason=finish_reason), chunk
