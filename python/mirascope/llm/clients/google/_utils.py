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
    """Convert mirascope content to Google Part format."""
    result = []
    for item in content:
        if item.type == "text":
            result.append({"text": item.text})
        else:
            raise NotImplementedError(
                f"Have not implemented conversion for {item.type}"
            )
    return result


def _decode_content_part(part: genai_types.Part) -> list[AssistantContentPart]:
    """Convert Google Part to mirascope AssistantContentPart."""
    if part.text:
        return [Text(text=part.text)]
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
        return []


def _encode_message(
    message: UserMessage | AssistantMessage,
) -> genai_types.ContentDict:
    """Convert a Mirascope message to Google ContentDict format.

    Args:
        message: A Mirascope message (system, user, or assistant)

    Returns:
        A single Google ContentDict
    """

    return {
        "role": "model" if message.role == "assistant" else message.role,
        "parts": _encode_content(message.content),
    }


def _encode_messages(
    messages: Sequence[UserMessage | AssistantMessage],
) -> genai_types.ContentListUnionDict:
    """Convert a sequence of Mirascope user or assistant Messages to Google ContentDict"""
    return [_encode_message(message) for message in messages]


def _decode_response(
    response: genai_types.GenerateContentResponse,
) -> tuple[AssistantMessage, FinishReason]:
    """Convert Google response to mirascope AssistantMessage and FinishReason."""
    if not response.candidates or not response.candidates[0].content:
        # Unclear under what circumstances this happens (if ever).
        # In testing, when generating no output at all, it creates a part with
        # no fields set.
        assistant_message = assistant(content=[])  # pragma: no cover
    else:
        candidate = response.candidates[0]
        content_parts = []
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                content_parts.extend(_decode_content_part(part))
        assistant_message = assistant(content=content_parts)

    finish_reason = FinishReason.UNKNOWN
    if response.candidates and response.candidates[0].finish_reason:
        reason = response.candidates[0].finish_reason
        finish_reason = GOOGLE_FINISH_REASON_MAP.get(reason, FinishReason.UNKNOWN)

    return (assistant_message, finish_reason)
