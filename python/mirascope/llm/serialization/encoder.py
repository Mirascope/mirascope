"""Serialization encoder for Mirascope responses."""

from collections.abc import Mapping
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version as get_version
from typing import TYPE_CHECKING, Any

import msgspec
from msgspec import UNSET

from ..content import (
    AssistantContentPart,
    Audio,
    Base64AudioSource as ContentBase64AudioSource,
    Base64DocumentSource as ContentBase64DocumentSource,
    Base64ImageSource as ContentBase64ImageSource,
    Document,
    Image,
    Text,
    TextDocumentSource as ContentTextDocumentSource,
    Thought,
    ToolCall,
    ToolOutput,
    URLDocumentSource as ContentURLDocumentSource,
    URLImageSource as ContentURLImageSource,
    UserContentPart,
)
from ..formatting import Format
from ..messages import AssistantMessage, Message, SystemMessage, UserMessage
from ..responses.finish_reason import FinishReason
from ..tools import BaseToolkit

if TYPE_CHECKING:
    from ..responses import RootResponse

from ._generated.response import (
    AssistantMessage as SerializedAssistantMessage,
    AudioContent,
    Base64AudioSource,
    Base64DocumentSource,
    Base64ImageSource,
    DocumentContent,
    FinishReason as SerializedFinishReason,
    ImageContent,
    Metadata,
    Mode as SerializedMode,
    SerializedFormat,
    SerializedResponse,
    SerializedToolSchema,
    SystemMessage as SerializedSystemMessage,
    TextContent,
    TextDocumentSource,
    ThoughtContent,
    ToolCallContent,
    ToolOutputContent,
    ToolParameterSchema,
    URLDocumentSource,
    URLImageSource,
    UserMessage as SerializedUserMessage,
)
from .version import CURRENT_VERSION


def encode(
    response: "RootResponse[Any, Any]",
    *,
    version: str = CURRENT_VERSION,
) -> bytes:
    """Encode a Response to JSON bytes.

    Args:
        response: The response to encode.
        version: The serialization format version (default: current version).

    Returns:
        JSON-encoded bytes representation of the response.
    """
    payload = _build_payload(response, version=version)
    return msgspec.json.encode(payload)


def encode_str(
    response: "RootResponse[Any, Any]",
    *,
    version: str = CURRENT_VERSION,
) -> str:
    """Encode a Response to a JSON string.

    Args:
        response: The response to encode.
        version: The serialization format version (default: current version).

    Returns:
        JSON string representation of the response.
    """
    return encode(response, version=version).decode("utf-8")


def _build_payload(
    response: "RootResponse[Any, Any]",
    *,
    version: str,
) -> SerializedResponse:
    """Build the serialization payload for a response."""
    return SerializedResponse(
        field_schema=f"mirascope/response/v{version.split('.')[0]}",
        version=version,
        type="response",
        provider=response.provider_id,
        model_id=response.model_id,
        messages=[_encode_message(m) for m in response.messages],
        metadata=Metadata(
            serialized_at=datetime.now(timezone.utc).isoformat(),
            mirascope_version=_get_mirascope_version(),
        ),
        finish_reason=_encode_finish_reason(response.finish_reason),
        params=_encode_params(response.params),
        tools=_encode_tools(response.toolkit),
        format=_encode_format(response.format),
    )


def _encode_finish_reason(
    finish_reason: FinishReason | None,
) -> SerializedFinishReason | None:
    """Encode a finish reason to a SerializedFinishReason."""
    if finish_reason is None:
        return None
    if finish_reason == FinishReason.MAX_TOKENS:
        return SerializedFinishReason.max_tokens
    elif finish_reason == FinishReason.REFUSAL:
        return SerializedFinishReason.refusal
    return None


def _encode_message(
    message: Message,
) -> SerializedSystemMessage | SerializedUserMessage | SerializedAssistantMessage:
    """Encode a message to a serialized message struct."""
    if isinstance(message, SystemMessage):
        return SerializedSystemMessage(
            content=[TextContent(text=message.content.text)],
        )
    elif isinstance(message, UserMessage):
        return SerializedUserMessage(
            content=[_encode_user_content_part(p) for p in message.content],
            name=message.name,
        )
    elif isinstance(message, AssistantMessage):
        return SerializedAssistantMessage(
            content=[_encode_assistant_content_part(p) for p in message.content],
            name=message.name,
            provider=message.provider_id,
            model_id=message.model_id,
            raw_message=message.raw_message,
        )
    else:
        raise TypeError(f"Unknown message type: {type(message)}")


def _encode_user_content_part(
    part: UserContentPart,
) -> TextContent | ImageContent | AudioContent | DocumentContent | ToolOutputContent:
    """Encode a user content part."""
    if isinstance(part, Text):
        return TextContent(text=part.text)
    elif isinstance(part, Image):
        return ImageContent(source=_encode_image_source(part.source))
    elif isinstance(part, Audio):
        return AudioContent(source=_encode_audio_source(part.source))
    elif isinstance(part, Document):
        return DocumentContent(source=_encode_document_source(part.source))
    elif isinstance(part, ToolOutput):
        return ToolOutputContent(
            id=part.id,
            name=part.name,
            value=part.value,
        )
    else:
        raise TypeError(f"Unknown user content part type: {type(part)}")


def _encode_assistant_content_part(
    part: AssistantContentPart,
) -> TextContent | ToolCallContent | ThoughtContent:
    """Encode an assistant content part."""
    if isinstance(part, Text):
        return TextContent(text=part.text)
    elif isinstance(part, ToolCall):
        return ToolCallContent(
            id=part.id,
            name=part.name,
            args=part.args,
        )
    elif isinstance(part, Thought):
        return ThoughtContent(thought=part.thought)
    else:
        raise TypeError(f"Unknown assistant content part type: {type(part)}")


def _encode_image_source(
    source: ContentBase64ImageSource | ContentURLImageSource,
) -> Base64ImageSource | URLImageSource:
    """Encode an image source."""
    if isinstance(source, ContentBase64ImageSource):
        return Base64ImageSource(
            data=source.data,
            mime_type=source.mime_type,
        )
    else:
        return URLImageSource(
            url=source.url,
        )


def _encode_audio_source(source: ContentBase64AudioSource) -> Base64AudioSource:
    """Encode an audio source."""
    return Base64AudioSource(
        type="base64_audio_source",
        data=source.data,
        mime_type=source.mime_type,
    )


def _encode_document_source(
    source: ContentBase64DocumentSource
    | ContentTextDocumentSource
    | ContentURLDocumentSource,
) -> Base64DocumentSource | TextDocumentSource | URLDocumentSource:
    """Encode a document source."""
    if isinstance(source, ContentBase64DocumentSource):
        return Base64DocumentSource(
            data=source.data,
            media_type=source.media_type,
        )
    elif isinstance(source, ContentTextDocumentSource):
        return TextDocumentSource(
            data=source.data,
            media_type=source.media_type,
        )
    else:
        return URLDocumentSource(
            url=source.url,
        )


def _encode_params(
    params: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    """Encode response params to a dictionary, preserving None vs empty dict."""
    if params is None:
        return None
    return dict(params)


def _get_mirascope_version() -> str:
    """Get the current Mirascope package version."""
    try:
        return get_version("mirascope")
    except PackageNotFoundError:
        return "unknown"


def _encode_tools(
    toolkit: BaseToolkit[Any],
) -> list[SerializedToolSchema] | None:
    """Encode toolkit tools to a list of serialized tool schemas.

    Args:
        toolkit: The toolkit containing tools to encode.

    Returns:
        A list of serialized tool schemas, or None if no tools.
    """
    if not toolkit.tools:
        return None

    result: list[SerializedToolSchema] = []
    for tool in toolkit.tools:
        defs = tool.parameters.defs if tool.parameters.defs is not None else UNSET
        parameters = ToolParameterSchema(
            properties=tool.parameters.properties,
            required=tool.parameters.required,
            additionalProperties=tool.parameters.additionalProperties,
            defs=defs,
        )

        result.append(
            SerializedToolSchema(
                name=tool.name,
                description=tool.description,
                parameters=parameters,
                strict=tool.strict,
            )
        )
    return result


def _encode_format(
    format_spec: Format[Any] | None,
) -> SerializedFormat | None:
    """Encode a format to a serialized format.

    Args:
        format_spec: The format to encode, or None.

    Returns:
        A serialized format, or None if no format.
    """
    if format_spec is None:
        return None

    mode = SerializedMode(format_spec.mode)
    return SerializedFormat(
        name=format_spec.name,
        schema=format_spec.schema,
        mode=mode,
        description=format_spec.description,
    )
