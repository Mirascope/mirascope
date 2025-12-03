"""Utilities for encoding Mirascope messages into GenAI semconv payloads."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import gen_ai_types

if TYPE_CHECKING:
    from typing import TypeAlias

    MessagePart: TypeAlias = (
        gen_ai_types.TextPart
        | gen_ai_types.ToolCallRequestPart
        | gen_ai_types.ToolCallResponsePart
        | gen_ai_types.BlobPart
        | gen_ai_types.FilePart
        | gen_ai_types.UriPart
        | gen_ai_types.ReasoningPart
        | gen_ai_types.GenericPart
    )


from .....llm.content import (
    Audio,
    Base64ImageSource,
    Document,
    Image,
    Text,
    Thought,
    ToolCall,
    ToolOutput,
)
from .....llm.formatting import FormattableT
from .....llm.messages import AssistantMessage, Message, SystemMessage
from .....llm.responses.finish_reason import FinishReason
from .....llm.responses.root_response import RootResponse
from .....llm.tools import ToolkitT
from .....llm.types import Jsonable


@dataclass(frozen=True, slots=True)
class OTelMessageSnapshot:
    """Structured view of system, input, and output messages."""

    system_instructions: gen_ai_types.SystemInstructions
    """Instructions to be executed prior to the conversation."""

    inputs: gen_ai_types.InputMessages
    """Messages to be sent to the model."""

    outputs: gen_ai_types.OutputMessages
    """Messages received from the model."""


def _serialize_message_parts(
    parts: Sequence[
        Text | ToolCall | ToolOutput[Jsonable] | Thought | Image | Audio | Document
    ],
) -> list[MessagePart]:
    """Serialize message content parts into GenAI-compliant dictionaries.

    Handles Text, ToolCall, ToolOutput, Thought, Image, Audio, Document,
    and str types.
    """
    serialized: list[MessagePart] = []
    for part in parts:
        match part:
            case Text():
                text_part: gen_ai_types.TextPart = {
                    "type": "text",
                    "content": part.text,
                }
                serialized.append(text_part)
            case ToolCall():
                try:
                    arguments = json.loads(part.args)
                except json.JSONDecodeError:  # pragma: no cover
                    arguments = ""
                tool_call_part: gen_ai_types.ToolCallRequestPart = {
                    "type": "tool_call",
                    "id": part.id,
                    "name": part.name,
                    "arguments": arguments,
                }
                serialized.append(tool_call_part)
            case ToolOutput():
                tool_output_part: gen_ai_types.ToolCallResponsePart = {
                    "type": "tool_call_response",
                    "id": part.id,
                    "response": part.value,
                }
                serialized.append(tool_output_part)
            case Thought():
                serialized.append(
                    gen_ai_types.ReasoningPart(type="reasoning", content=part.thought)
                )
            case Image():
                if isinstance(part.source, Base64ImageSource):
                    image = gen_ai_types.BlobPart(
                        type="blob",
                        modality="image",
                        mime_type=part.source.mime_type,
                        content=part.source.data,
                    )
                else:
                    image = gen_ai_types.UriPart(
                        type="uri", modality="image", uri=part.source.url
                    )
                serialized.append(image)
            case Audio():
                serialized.append(
                    gen_ai_types.BlobPart(
                        type="blob",
                        modality="audio",
                        mime_type=part.source.mime_type,
                        content=part.source.data,
                    )
                )
            case Document():  # pragma: no cover
                raise NotImplementedError(
                    "Document serialization is not yet supported by any provider. "
                    "This will be implemented when provider support is added."
                )
    return serialized


def _serialize_message(message: Message) -> gen_ai_types.ChatMessage:
    """Serialize a Mirascope message into a GenAI ChatMessage."""
    content_parts = _serialize_message_parts(
        message.content if not isinstance(message, SystemMessage) else [message.content]
    )
    serialized: gen_ai_types.ChatMessage = {
        "role": message.role,
        "parts": content_parts,
    }
    name = getattr(message, "name", None)
    if name:
        serialized["name"] = name
    return serialized


def map_finish_reason(
    reason: FinishReason | None,
) -> gen_ai_types.FinishReason:
    """Map a finish reason to a GenAI finish reason."""
    if reason is None:
        return "stop"
    elif reason == FinishReason.MAX_TOKENS:
        return "length"
    elif reason == FinishReason.REFUSAL:  # pragma: no cover
        return "content_filter"
    raise ValueError(f"Unknown finish reason: {reason}")  # pragma: no cover


def _serialize_output_message(
    message: AssistantMessage, finish_reason: FinishReason | None
) -> gen_ai_types.OutputMessage:
    """Serialize an assistant message into a GenAI OutputMessage with finish_reason."""
    chat_message = _serialize_message(message)
    output_message: gen_ai_types.OutputMessage = {
        "role": chat_message["role"],
        "parts": chat_message["parts"],
        "finish_reason": map_finish_reason(finish_reason),
    }
    if "name" in chat_message:
        output_message["name"] = chat_message["name"]
    return output_message


def split_request_messages(
    messages: Sequence[Message],
) -> tuple[gen_ai_types.SystemInstructions, gen_ai_types.InputMessages]:
    """Return serialized system instructions and non-system input messages.

    System messages are flattened into a list of parts (not wrapped in message objects),
    while other messages are serialized as complete ChatMessage objects.
    """
    system_instructions: gen_ai_types.SystemInstructions = []
    inputs: gen_ai_types.InputMessages = []
    for message in messages:
        if message.role == "system":
            # System messages contribute only their parts (flattened)
            parts = _serialize_message_parts(
                [message.content]
                if isinstance(message, SystemMessage)
                else message.content
            )
            system_instructions.extend(parts)
        else:
            # Non-system messages are serialized as full ChatMessage objects
            serialized = _serialize_message(message)
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


def snapshot_from_root_response(
    response: RootResponse[ToolkitT, FormattableT | None],
    *,
    request_messages: Sequence[Message] | None = None,
) -> OTelMessageSnapshot:
    """Build a snapshot directly from a `RootResponse`.

    Args:
        response: The response that includes the entire conversation history.
        request_messages: Optional explicit request message sequence. Defaults to all
            but the final assistant message inside `response.messages`.
    """

    assistant_message = response.messages[-1]
    if not isinstance(assistant_message, AssistantMessage):  # pragma: no cover
        raise TypeError("Final response message must be an AssistantMessage")

    return snapshot_from_response_messages(
        request_messages=request_messages or response.messages[:-1],
        assistant_message=assistant_message,
        finish_reason=response.finish_reason,
    )
