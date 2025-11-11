"""Utilities for serializing Mirascope messages into GenAI semconv payloads."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from opentelemetry.semconv._incubating.attributes import (
    gen_ai_attributes as GenAIAttributes,
)

from ._json import json_dumps

if TYPE_CHECKING:
    from typing import TypeAlias

    JsonPrimitive: TypeAlias = str | int | float | bool | None
    JsonValue: TypeAlias = (
        JsonPrimitive | Mapping[str, "JsonValue"] | Sequence["JsonValue"]
    )
    JsonDict: TypeAlias = dict[str, JsonValue]
else:
    JsonDict = dict

from ..content import (
    Audio,
    Base64AudioSource,
    Base64DocumentSource,
    Base64ImageSource,
    Document,
    Image,
    Text,
    TextDocumentSource,
    Thought,
    ToolCall,
    ToolOutput,
    URLDocumentSource,
    URLImageSource,
)
from ..messages import AssistantMessage, Message, SystemMessage
from ..responses.finish_reason import FinishReason
from ..responses.root_response import RootResponse


@dataclass(frozen=True, slots=True)
class OTelMessageSnapshot:
    """Structured view of system, input, and output messages."""

    system_instructions: list[JsonDict]
    inputs: list[JsonDict]
    outputs: list[JsonDict]

    def as_json(self) -> dict[str, str]:
        """Return JSON-encoded payloads for each populated channel."""

        payload: dict[str, str] = {}
        if self.system_instructions:
            payload[GenAIAttributes.GEN_AI_SYSTEM_INSTRUCTIONS] = json_dumps(
                self.system_instructions,
            )
        if self.inputs:
            payload[GenAIAttributes.GEN_AI_INPUT_MESSAGES] = json_dumps(self.inputs)
        if self.outputs:
            payload[GenAIAttributes.GEN_AI_OUTPUT_MESSAGES] = json_dumps(self.outputs)
        return payload


def split_request_messages(
    messages: Sequence[Message],
) -> tuple[list[JsonDict], list[JsonDict]]:
    """Return serialized system instructions and non-system input messages."""

    system_instructions: list[JsonDict] = []
    inputs: list[JsonDict] = []
    for message in messages:
        serialized = _serialize_message(message)
        if message.role == "system":
            system_instructions.append(serialized)
        else:
            inputs.append(serialized)
    return system_instructions, inputs


def snapshot_from_response_messages(
    *,
    request_messages: Sequence[Message],
    assistant_message: AssistantMessage,
    finish_reason: FinishReason | None,
) -> OTelMessageSnapshot:
    """Build a snapshot using the request/response boundary for a call."""

    system_instructions, inputs = split_request_messages(request_messages)
    outputs = [_serialize_output_message(assistant_message, finish_reason)]
    return OTelMessageSnapshot(
        system_instructions=system_instructions,
        inputs=inputs,
        outputs=outputs,
    )


def _serialize_message(message: Message) -> JsonDict:
    content_parts = _serialize_message_parts(
        message.content if not isinstance(message, SystemMessage) else [message.content]
    )
    serialized: JsonDict = {
        "role": message.role,
        "parts": content_parts,
    }
    name = getattr(message, "name", None)
    if name:
        serialized["name"] = name
    return serialized


def _serialize_output_message(
    message: AssistantMessage, finish_reason: FinishReason | None
) -> JsonDict:
    serialized = _serialize_message(message)
    serialized["finish_reason"] = _map_finish_reason(finish_reason)
    return serialized


def _serialize_message_parts(
    parts: Sequence[Text | ToolCall | ToolOutput | Thought | Image | Audio | Document],
) -> list[JsonDict]:
    """Serialize message content parts into GenAI-compliant dictionaries.

    Handles Text, ToolCall, ToolOutput, Thought, Image, Audio, Document,
    and str types.
    """
    serialized: list[JsonDict] = []
    for part in parts:
        if isinstance(part, Text):
            serialized.append({"type": "text", "content": part.text})
        elif isinstance(part, ToolCall):
            serialized.append(
                {
                    "type": "tool_call",
                    "id": part.id,
                    "name": part.name,
                    "arguments": _maybe_parse_json(part.args),
                }
            )
        elif isinstance(part, ToolOutput):
            serialized.append(
                {
                    "type": "tool_call_response",
                    "id": part.id,
                    "name": part.name,
                    "response": part.value,
                }
            )
        elif isinstance(part, Thought):
            serialized.append({"type": "reasoning", "content": part.thought})
        elif isinstance(part, Image):
            serialized.append(_serialize_image(part))
        elif isinstance(part, Audio):
            serialized.append(_serialize_audio(part))
        elif isinstance(part, Document):
            serialized.append(_serialize_document(part))
    return serialized


def _serialize_image(image: Image) -> JsonDict:
    source = image.source
    if isinstance(source, Base64ImageSource):
        return {
            "type": "blob",
            "modality": "image",
            "mime_type": source.mime_type,
            "content": source.data,
        }
    if isinstance(source, URLImageSource):
        return {
            "type": "uri",
            "modality": "image",
            "uri": source.url,
        }
    return {
        "type": "image",
        "source": str(source),
    }


def _serialize_audio(audio: Audio) -> JsonDict:
    source = audio.source
    if isinstance(source, Base64AudioSource):
        return {
            "type": "blob",
            "modality": "audio",
            "mime_type": source.mime_type,
            "content": source.data,
        }
    return {
        "type": "audio",
        "source": str(source),
    }


def _serialize_document(document: Document) -> JsonDict:
    source = document.source
    if isinstance(source, URLDocumentSource):
        return {
            "type": "uri",
            "modality": "document",
            "uri": source.url,
        }
    if isinstance(source, Base64DocumentSource):
        return {
            "type": "blob",
            "modality": "document",
            "mime_type": source.media_type,
            "content": source.data,
        }
    if isinstance(source, TextDocumentSource):
        return {
            "type": "text",
            "content": source.data,
            "mime_type": source.media_type,
        }
    return {
        "type": "generic",
        "modality": "document",
        "source": str(source),
    }


def _map_finish_reason(reason: FinishReason | None) -> str:
    if reason is None:
        return "stop"
    if reason == FinishReason.MAX_TOKENS:
        return "length"
    if reason == FinishReason.REFUSAL:
        return "content_filter"
    raise ValueError(f"Unknown finish reason: {reason}")  # pragma: no cover


def _maybe_parse_json(value: str) -> str | int | float | bool | None | dict | list:
    """Parse JSON string if valid, otherwise return original string."""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError, TypeError):
        return value


def finish_reason_to_string(reason: FinishReason | None) -> str:
    """Public helper for mapping finish reasons to GenAI enumerations."""

    return _map_finish_reason(reason)


def serialize_response_messages(response: RootResponse) -> dict[str, str]:
    """Return OTEL-ready JSON payloads for a response."""

    if not response.messages:
        return {}

    assistant_message = response.messages[-1]
    if not isinstance(assistant_message, AssistantMessage):  # pragma: no cover
        raise TypeError("Final response message must be an AssistantMessage")

    snapshot = snapshot_from_response_messages(
        request_messages=response.messages[:-1],
        assistant_message=assistant_message,
        finish_reason=response.finish_reason,
    )
    return snapshot.as_json()
