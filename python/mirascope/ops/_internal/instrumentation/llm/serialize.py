"""Mirascope-specific serialization for span attributes."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any, Protocol

from opentelemetry.util.types import AttributeValue

from .....llm import (
    AnyToolSchema,
    AssistantMessage,
    Audio,
    Base64ImageSource,
    Document,
    Image,
    Jsonable,
    Message,
    ProviderTool,
    RootResponse,
    SystemMessage,
    Text,
    Thought,
    ToolCall,
    ToolOutput,
    Usage,
    UserMessage,
)
from .....llm.content.document import Base64DocumentSource, TextDocumentSource
from ...utils import json_dumps
from .cost import calculate_cost_async, calculate_cost_sync

logger = logging.getLogger(__name__)


class SpanProtocol(Protocol):
    """Protocol for span objects that support setting attributes."""

    def set(self, **attributes: AttributeValue) -> None:
        """Set attributes on the span."""
        ...


def _serialize_content_part(
    part: Text | ToolCall | Thought | Image | Audio | Document | ToolOutput[Jsonable],
) -> dict[str, Jsonable]:
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


def _serialize_message(message: Message) -> dict[str, Jsonable]:
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


def _serialize_tool(tool: AnyToolSchema | ProviderTool) -> dict[str, Jsonable]:
    if isinstance(tool, ProviderTool):
        return {"name": tool.name, "type": "extension"}
    result: dict[str, Jsonable] = {
        "name": tool.name,
        "description": tool.description,
        "type": "function",
        "parameters": tool.parameters.model_dump(by_alias=True, mode="json"),
    }
    if tool.strict is not None:
        result["strict"] = tool.strict
    return result


def serialize_tools(tools: Sequence[AnyToolSchema | ProviderTool]) -> str | None:
    """Serialize a sequence of Mirascope tools"""
    if not tools:
        return None
    return json_dumps([_serialize_tool(t) for t in tools])


def serialize_mirascope_cost(
    input_cost: float,
    output_cost: float,
    total_cost: float,
    cache_read_cost: float | None = None,
    cache_write_cost: float | None = None,
) -> str:
    """Serialize cost to JSON for span attributes.

    All costs are in centicents (1 centicent = $0.0001).
    Consumers can divide by 10,000 to get dollar amounts.
    """
    return json_dumps(
        {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "cache_read_cost": cache_read_cost,
            "cache_write_cost": cache_write_cost,
            "total_cost": total_cost,
        }
    )


def attach_mirascope_response(
    span: SpanProtocol, response: RootResponse[Any, Any]
) -> None:
    """Attach Mirascope-specific response attributes to a span.

    Sets the following attributes:
    - mirascope.trace.output: Pretty-printed response
    - mirascope.response.messages: Serialized input messages (excluding final assistant message)
    - mirascope.response.content: Serialized response content
    - mirascope.response.usage: Serialized usage (if available)
    - mirascope.response.cost: Serialized cost (if available)
    """
    span.set(
        **{
            "mirascope.response.provider_id": response.provider_id,
            "mirascope.response.model_id": response.model_id,
            "mirascope.trace.output": response.pretty(),
            "mirascope.response.messages": serialize_mirascope_messages(
                response.messages[:-1]
            ),
            "mirascope.response.content": serialize_mirascope_content(response.content),
        }
    )
    if (usage_json := serialize_mirascope_usage(response.usage)) is not None:
        span.set(**{"mirascope.response.usage": usage_json})
        logger.debug("Attached usage to span")
    else:
        logger.debug("No usage available, skipping cost calculation")

    # Calculate and attach cost if usage is available
    if response.usage is not None:
        logger.debug("Attempting cost calculation (sync)")
        cost = calculate_cost_sync(
            response.provider_id, response.model_id, response.usage
        )
        if cost is not None:
            span.set(
                **{
                    "mirascope.response.cost": serialize_mirascope_cost(
                        input_cost=cost.input_cost_centicents,
                        output_cost=cost.output_cost_centicents,
                        total_cost=cost.total_cost_centicents,
                        cache_read_cost=cost.cache_read_cost_centicents,
                        cache_write_cost=cost.cache_write_cost_centicents,
                    )
                }
            )
            logger.debug(
                "Attached cost to span: total=%s centicents", cost.total_cost_centicents
            )
        else:
            logger.debug("Cost calculation returned None, not attaching cost to span")


async def attach_mirascope_response_async(
    span: SpanProtocol, response: RootResponse[Any, Any]
) -> None:
    """Attach Mirascope-specific response attributes to a span (async version).

    Sets the following attributes:
    - mirascope.trace.output: Pretty-printed response
    - mirascope.response.messages: Serialized input messages (excluding final assistant message)
    - mirascope.response.content: Serialized response content
    - mirascope.response.usage: Serialized usage (if available)
    - mirascope.response.cost: Serialized cost (if available)
    """
    span.set(
        **{
            "mirascope.response.provider_id": response.provider_id,
            "mirascope.response.model_id": response.model_id,
            "mirascope.trace.output": response.pretty(),
            "mirascope.response.messages": serialize_mirascope_messages(
                response.messages[:-1]
            ),
            "mirascope.response.content": serialize_mirascope_content(response.content),
        }
    )
    if (usage_json := serialize_mirascope_usage(response.usage)) is not None:
        span.set(**{"mirascope.response.usage": usage_json})
        logger.debug("Attached usage to span (async)")
    else:
        logger.debug("No usage available, skipping cost calculation (async)")

    # Calculate and attach cost if usage is available (async)
    if response.usage is not None:
        logger.debug("Attempting cost calculation (async)")
        cost = await calculate_cost_async(
            response.provider_id, response.model_id, response.usage
        )
        if cost is not None:
            span.set(
                **{
                    "mirascope.response.cost": serialize_mirascope_cost(
                        input_cost=cost.input_cost_centicents,
                        output_cost=cost.output_cost_centicents,
                        total_cost=cost.total_cost_centicents,
                        cache_read_cost=cost.cache_read_cost_centicents,
                        cache_write_cost=cost.cache_write_cost_centicents,
                    )
                }
            )
            logger.debug(
                "Attached cost to span (async): total=%s centicents",
                cost.total_cost_centicents,
            )
        else:
            logger.debug(
                "Cost calculation returned None, not attaching cost to span (async)"
            )
