"""Mirascope-specific serialization for span attributes."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol

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
from .....llm.content.document import Base64DocumentSource, TextDocumentSource
from .....llm.messages import AssistantMessage, Message, SystemMessage, UserMessage
from .....llm.responses.usage import Usage
from ...utils import json_dumps

if TYPE_CHECKING:
    from opentelemetry.util.types import AttributeValue

    from .....llm.responses.root_response import RootResponse
    from .....llm.types import Jsonable


class SpanProtocol(Protocol):
    """Protocol for span objects that support setting attributes."""

    def set(self, **attributes: AttributeValue) -> None:
        """Set attributes on the span."""
        ...


def _serialize_content_part(
    part: Text | ToolCall | Thought | Image | Audio | Document | ToolOutput[Jsonable],
) -> dict[str, Any]:
    """Serialize a single content part to a dict matching the Mirascope dataclass structure."""
    if isinstance(part, Text):
        return {"type": "text", "text": part.text}
    elif isinstance(part, ToolCall):
        return {
            "type": "tool_call",
            "id": part.id,
            "name": part.name,
            "args": part.args,
        }
    elif isinstance(part, Thought):
        return {"type": "thought", "thought": part.thought}
    elif isinstance(part, ToolOutput):
        return {
            "type": "tool_output",
            "id": part.id,
            "name": part.name,
            "result": part.result,
        }
    elif isinstance(part, Image):
        if isinstance(part.source, Base64ImageSource):
            return {
                "type": "image",
                "source": {
                    "type": "base64_image_source",
                    "mime_type": part.source.mime_type,
                    "data": part.source.data,
                },
            }
        else:  # URLImageSource
            return {
                "type": "image",
                "source": {"type": "url_image_source", "url": part.source.url},
            }
    elif isinstance(part, Audio):
        return {
            "type": "audio",
            "source": {
                "type": "base64_audio_source",
                "mime_type": part.source.mime_type,
                "data": part.source.data,
            },
        }
    elif isinstance(part, Document):
        # Document has multiple source types - serialize based on actual type
        if isinstance(part.source, Base64DocumentSource):
            return {
                "type": "document",
                "source": {
                    "type": "base64_document_source",
                    "data": part.source.data,
                    "media_type": part.source.media_type,
                },
            }
        elif isinstance(part.source, TextDocumentSource):
            return {
                "type": "document",
                "source": {
                    "type": "text_document_source",
                    "data": part.source.data,
                    "media_type": part.source.media_type,
                },
            }
        else:  # URLDocumentSource
            return {
                "type": "document",
                "source": {
                    "type": "url_document_source",
                    "url": part.source.url,
                },
            }
    return {"type": "unknown"}  # pragma: no cover


def _serialize_message(message: Message) -> dict[str, Any]:
    """Serialize a Message to a dict matching the Mirascope dataclass structure."""
    if isinstance(message, SystemMessage):
        return {
            "role": "system",
            "content": _serialize_content_part(message.content),
        }
    elif isinstance(message, UserMessage):
        return {
            "role": "user",
            "content": [_serialize_content_part(p) for p in message.content],
            "name": message.name,
        }
    elif isinstance(message, AssistantMessage):
        return {
            "role": "assistant",
            "content": [_serialize_content_part(p) for p in message.content],
            "name": message.name,
        }
    return {"role": "unknown"}  # pragma: no cover


def serialize_mirascope_messages(messages: Sequence[Message]) -> str:
    """Serialize input messages to JSON for span attributes."""
    return json_dumps([_serialize_message(m) for m in messages])


def serialize_mirascope_content(
    content: Sequence[Text | ToolCall | Thought],
) -> str:
    """Serialize response content to JSON for span attributes."""
    return json_dumps([_serialize_content_part(p) for p in content])


def serialize_mirascope_usage(usage: Usage | None) -> AttributeValue | None:
    """Serialize response usage to JSON for span attributes. Returns None if usage is None."""
    if usage is None:
        return None
    return json_dumps(
        {
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "cache_read_tokens": usage.cache_read_tokens,
            "cache_write_tokens": usage.cache_write_tokens,
            "reasoning_tokens": usage.reasoning_tokens,
            "total_tokens": usage.total_tokens,
        }
    )


def attach_mirascope_response(
    span: SpanProtocol, response: RootResponse[Any, Any]
) -> None:
    """Attach Mirascope-specific response attributes to a span.

    Sets the following attributes:
    - mirascope.trace.output: Pretty-printed response
    - mirascope.messages: Serialized input messages (excluding final assistant message)
    - mirascope.response.content: Serialized response content
    - mirascope.response.usage: Serialized usage (if available)
    """
    span.set(
        **{
            "mirascope.provider_id": response.provider_id,
            "mirascope.model_id": response.model_id,
            "mirascope.trace.output": response.pretty(),
            "mirascope.messages": serialize_mirascope_messages(response.messages[:-1]),
            "mirascope.response.content": serialize_mirascope_content(response.content),
        }
    )
    if (usage_json := serialize_mirascope_usage(response.usage)) is not None:
        span.set(**{"mirascope.response.usage": usage_json})
