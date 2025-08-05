"""Google message types and conversion utilities."""

from collections.abc import Sequence

from google.genai import types as genai_types

from ...content import (
    AssistantContentPart,
    ContentPart,
    Text,
)
from ...messages import AssistantMessage, UserMessage, assistant
from ...responses import FinishReason

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
        return Text(text=part.text.strip("\n"))
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


def _encode_message(
    message: UserMessage | AssistantMessage,
) -> genai_types.ContentDict:
    """Returns a Google `ContentDict` converted from a Mirascope `Message`"""

    return {
        "role": "model" if message.role == "assistant" else message.role,
        "parts": _encode_content(message.content),
    }


def encode_messages(
    messages: Sequence[UserMessage | AssistantMessage],
) -> genai_types.ContentListUnionDict:
    """Returns a `ContentListUnionDict` converted from a sequence of user or assistant `Messages`s"""
    return [_encode_message(message) for message in messages]


def decode_response(
    response: genai_types.GenerateContentResponse,
) -> tuple[AssistantMessage, FinishReason]:
    """Returns an `AssistantMessage` and `FinishReason` extracted from a `GenerateContentResponse`"""
    if not response.candidates or not response.candidates[0].content:
        # Unclear under what circumstances this happens (if ever).
        # In testing, when generating no output at all, it creates a part with
        # no fields set.
        return assistant(content=[]), FinishReason.UNKNOWN  # pragma: no cover

    candidate = response.candidates[0]
    content_parts = []
    if candidate.content and candidate.content.parts:
        for part in candidate.content.parts:
            decoded_part = _decode_content_part(part)
            if decoded_part:
                content_parts.append(decoded_part)
    assistant_message = assistant(content=content_parts)
    if reason := candidate.finish_reason:
        finish_reason = GOOGLE_FINISH_REASON_MAP.get(reason, FinishReason.UNKNOWN)
    else:
        finish_reason = FinishReason.UNKNOWN  # pragma: no cover
    return assistant_message, finish_reason
