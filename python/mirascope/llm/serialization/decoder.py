"""Deserialization decoder for Mirascope responses."""

import json
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast, overload

import msgspec

if TYPE_CHECKING:
    from ..providers import Params, ProviderId

from ..content import (
    AssistantContentPart,
    Audio as ContentAudio,
    Base64AudioSource as ContentBase64AudioSource,
    Base64DocumentSource as ContentBase64DocumentSource,
    Base64ImageSource as ContentBase64ImageSource,
    Document as ContentDocument,
    Image as ContentImage,
    ImageMimeType,
    Text,
    TextDocumentSource as ContentTextDocumentSource,
    Thought as ContentThought,
    ToolCall as ContentToolCall,
    ToolOutput as ContentToolOutput,
    URLDocumentSource as ContentURLDocumentSource,
    URLImageSource as ContentURLImageSource,
    UserContentPart,
)
from ..content.audio import AudioMimeType
from ..content.document import DocumentBase64MimeType, DocumentTextMimeType
from ..formatting import Format, FormattableT
from ..messages import AssistantMessage, Message, SystemMessage, UserMessage
from ..responses.finish_reason import FinishReason
from ..responses.response import Response
from ..tools import Tool, Toolkit
from ._generated.response import (
    AssistantMessage as SerializedAssistantMessage,
    AudioContent,
    Base64AudioSource,
    Base64DocumentSource,
    Base64ImageSource,
    DocumentContent,
    FinishReason as SerializedFinishReason,
    ImageContent,
    SerializedFormat,
    SerializedResponse,
    SerializedToolSchema,
    SystemMessage as SerializedSystemMessage,
    TextContent,
    TextDocumentSource,
    ThoughtContent,
    ToolCallContent,
    ToolOutputContent,
    URLDocumentSource,
    URLImageSource,
    UserMessage as SerializedUserMessage,
)
from .exceptions import (
    IncompatibleFormatError,
    IncompatibleToolsError,
    IncompatibleVersionError,
    InvalidSerializedDataError,
    UnknownMessageRoleError,
)
from .version import CURRENT_VERSION, SerializationVersion


@overload
def decode(data: str | bytes | SerializedResponse) -> Response[None]: ...


@overload
def decode(
    data: str | bytes | SerializedResponse,
    *,
    tools: Sequence[Tool] | Toolkit | None = None,
    format: Format[FormattableT] | None = None,
) -> Response[FormattableT]: ...


def decode(
    data: str | bytes | SerializedResponse,
    *,
    tools: Sequence[Tool] | Toolkit | None = None,
    format: Format[FormattableT] | None = None,
) -> Response[FormattableT] | Response[None]:
    """Decode serialized data to a Response.

    Args:
        data: Data to decode. Can be JSON bytes, JSON string, or a SerializedResponse.
        tools: Optional tools to attach to the decoded response. If provided,
            validates that tools are a superset of the serialized tools.
        format: Optional format to attach to the decoded response. If provided,
            validates that the format schema matches the serialized format.

    Returns:
        A Response instance reconstructed from the serialized data.

    Raises:
        IncompatibleVersionError: If the serialized data uses an incompatible version.
        InvalidSerializedDataError: If the data is malformed.
        SchemaMismatchError: If provided tools/format don't match serialized schemas.
    """
    if isinstance(data, SerializedResponse):
        return _decode_payload(data, tools=tools, format=format)

    if isinstance(data, str):
        data = data.encode("utf-8")

    try:
        payload = msgspec.json.decode(data, type=SerializedResponse)
    except msgspec.ValidationError as e:
        raise InvalidSerializedDataError(f"Invalid serialized data: {e}") from e
    except msgspec.DecodeError as e:
        raise InvalidSerializedDataError(f"Invalid JSON: {e}") from e

    return _decode_payload(payload, tools=tools, format=format)


def _decode_payload(
    payload: SerializedResponse,
    *,
    tools: Sequence[Tool] | Toolkit | None = None,
    format: Format[FormattableT] | None = None,
) -> Response[FormattableT] | Response[None]:
    """Decode a payload to a Response."""
    _validate_version(payload.version)
    _validate_schema(payload.field_schema, payload.version)

    if payload.type != "response":
        raise InvalidSerializedDataError(f"Unknown response type: {payload.type}")

    return _decode_response(payload, tools=tools, format=format)


def _validate_version(version_str: str) -> None:
    """Validate the serialization format version."""
    try:
        found_version = SerializationVersion.parse(version_str)
    except ValueError as e:
        raise InvalidSerializedDataError(
            f"Invalid version format: {version_str}"
        ) from e

    current_version = SerializationVersion.parse(CURRENT_VERSION)

    if not found_version.is_compatible_with(current_version):
        raise IncompatibleVersionError(
            f"Cannot decode version {found_version} with decoder version {current_version}",
            found_version=str(found_version),
            expected_version=str(current_version),
        )


def _validate_schema(schema: str, version: str) -> None:
    """Validate that the schema identifier matches the expected format."""
    major = version.split(".")[0]
    expected_schema = f"mirascope/response/v{major}"
    if schema != expected_schema:
        raise InvalidSerializedDataError(
            f"Schema mismatch: expected '{expected_schema}', got '{schema}'"
        )


def _decode_response(
    payload: SerializedResponse,
    *,
    tools: Sequence[Tool] | Toolkit | None = None,
    format: Format[FormattableT] | None = None,
) -> Response[FormattableT] | Response[None]:
    """Decode a response payload to a Response instance."""
    messages = _decode_messages(payload.messages)

    if not messages:
        raise InvalidSerializedDataError("Response must have at least one message")

    last_message = messages[-1]
    if not isinstance(last_message, AssistantMessage):
        raise InvalidSerializedDataError(
            "Last message must be an AssistantMessage, "
            f"got {type(last_message).__name__}"
        )

    input_messages = messages[:-1]
    assistant_message = last_message

    finish_reason = _decode_finish_reason(payload.finish_reason)

    raw_params: dict[str, Any] | None = None
    if not isinstance(payload.params, msgspec.UnsetType):
        raw_params = payload.params
    params = cast("Params", raw_params if raw_params is not None else {})

    serialized_tools: list[SerializedToolSchema] | None = None
    if not isinstance(payload.tools, msgspec.UnsetType):
        serialized_tools = payload.tools

    serialized_format: SerializedFormat | None = None
    if not isinstance(payload.format, msgspec.UnsetType):
        serialized_format = payload.format

    _validate_tools_schema(serialized_tools, tools)
    _validate_format_schema(serialized_format, format)

    return Response(
        raw=None,
        provider_id=cast("ProviderId", payload.provider),
        model_id=payload.model_id,
        provider_model_name=payload.model_id,
        params=params,
        tools=tools,
        format=format,
        input_messages=input_messages,
        assistant_message=assistant_message,
        finish_reason=finish_reason,
    )


def _decode_messages(
    messages_data: list[
        SerializedSystemMessage | SerializedUserMessage | SerializedAssistantMessage
    ],
) -> list[Message]:
    """Decode a list of serialized messages to Message instances."""
    return [_decode_message(m) for m in messages_data]


def _decode_message(
    data: SerializedSystemMessage | SerializedUserMessage | SerializedAssistantMessage,
) -> Message:
    """Decode a serialized message to a Message instance."""
    if isinstance(data, SerializedSystemMessage):
        return _decode_system_message(data)
    elif isinstance(data, SerializedUserMessage):
        return _decode_user_message(data)
    elif isinstance(data, SerializedAssistantMessage):
        return _decode_assistant_message(data)
    else:
        raise UnknownMessageRoleError(str(type(data).__name__))


def _decode_system_message(data: SerializedSystemMessage) -> SystemMessage:
    """Decode a system message to a SystemMessage instance."""
    if not data.content:
        raise InvalidSerializedDataError("SystemMessage must have content")

    first_content = data.content[0]
    if not isinstance(first_content, TextContent):
        raise InvalidSerializedDataError(
            f"SystemMessage content must be Text, got {type(first_content).__name__}"
        )

    return SystemMessage(content=Text(text=first_content.text))


def _decode_user_message(data: SerializedUserMessage) -> UserMessage:
    """Decode a user message to a UserMessage instance."""
    content = [_decode_user_content_part(c) for c in data.content]

    name: str | None = None
    if not isinstance(data.name, msgspec.UnsetType):
        name = data.name

    return UserMessage(
        content=content,
        name=name,
    )


def _decode_assistant_message(data: SerializedAssistantMessage) -> AssistantMessage:
    """Decode an assistant message to an AssistantMessage instance."""
    content = [_decode_assistant_content_part(c) for c in data.content]

    name: str | None = None
    if not isinstance(data.name, msgspec.UnsetType):
        name = data.name

    provider_id: "ProviderId | None" = None
    if not isinstance(data.provider, msgspec.UnsetType):
        provider_id = cast("ProviderId", data.provider) if data.provider else None

    model_id: str | None = None
    if not isinstance(data.model_id, msgspec.UnsetType):
        model_id = data.model_id

    raw_message: Any = None
    if not isinstance(data.raw_message, msgspec.UnsetType):
        raw_message = data.raw_message

    return AssistantMessage(
        content=content,
        name=name,
        provider_id=provider_id,
        model_id=model_id,
        provider_model_name=model_id,
        raw_message=raw_message,
    )


def _decode_user_content_part(
    data: TextContent
    | ImageContent
    | AudioContent
    | DocumentContent
    | ToolOutputContent,
) -> UserContentPart:
    """Decode a user content part."""
    if isinstance(data, TextContent):
        return Text(text=data.text)
    elif isinstance(data, ImageContent):
        return ContentImage(source=_decode_image_source(data.source))
    elif isinstance(data, AudioContent):
        return ContentAudio(source=_decode_audio_source(data.source))
    elif isinstance(data, DocumentContent):
        return ContentDocument(source=_decode_document_source(data.source))
    elif isinstance(data, ToolOutputContent):
        return ContentToolOutput(id=data.id, name=data.name, value=data.value)
    else:
        raise InvalidSerializedDataError(f"Unknown user content type: {type(data)}")


def _decode_assistant_content_part(
    data: TextContent | ToolCallContent | ThoughtContent,
) -> AssistantContentPart:
    """Decode an assistant content part."""
    if isinstance(data, TextContent):
        return Text(text=data.text)
    elif isinstance(data, ToolCallContent):
        args = data.args if isinstance(data.args, str) else json.dumps(data.args)
        return ContentToolCall(id=data.id, name=data.name, args=args)
    elif isinstance(data, ThoughtContent):
        return ContentThought(thought=data.thought)
    else:
        raise InvalidSerializedDataError(
            f"Unknown assistant content type: {type(data)}"
        )


def _decode_image_source(
    source: Base64ImageSource | URLImageSource,
) -> ContentBase64ImageSource | ContentURLImageSource:
    """Decode an image source."""
    if isinstance(source, Base64ImageSource):
        return ContentBase64ImageSource(
            type="base64_image_source",
            data=source.data,
            mime_type=cast(ImageMimeType, source.mime_type),
        )
    else:
        return ContentURLImageSource(
            type="url_image_source",
            url=source.url,
        )


def _decode_audio_source(source: Base64AudioSource) -> ContentBase64AudioSource:
    """Decode an audio source."""
    return ContentBase64AudioSource(
        type="base64_audio_source",
        data=source.data,
        mime_type=cast(AudioMimeType, source.mime_type),
    )


def _decode_document_source(
    source: Base64DocumentSource | TextDocumentSource | URLDocumentSource,
) -> ContentBase64DocumentSource | ContentTextDocumentSource | ContentURLDocumentSource:
    """Decode a document source."""
    if isinstance(source, Base64DocumentSource):
        return ContentBase64DocumentSource(
            type="base64_document_source",
            data=source.data,
            media_type=cast(DocumentBase64MimeType, source.media_type),
        )
    elif isinstance(source, TextDocumentSource):
        return ContentTextDocumentSource(
            type="text_document_source",
            data=source.data,
            media_type=cast(DocumentTextMimeType, source.media_type),
        )
    else:
        return ContentURLDocumentSource(
            type="url_document_source",
            url=source.url,
        )


def _decode_finish_reason(
    value: SerializedFinishReason | None | msgspec.UnsetType,
) -> FinishReason | None:
    """Decode a finish reason to a FinishReason enum value."""
    if value is None or isinstance(value, msgspec.UnsetType):
        return None

    if value == SerializedFinishReason.max_tokens:
        return FinishReason.MAX_TOKENS
    elif value == SerializedFinishReason.refusal:
        return FinishReason.REFUSAL
    return None


def _validate_tools_schema(
    serialized_tools: list[SerializedToolSchema] | None,
    provided_tools: Sequence[Tool] | Toolkit | None,
) -> None:
    """Validate that provided tools are a superset of serialized tools.

    Args:
        serialized_tools: Tool schemas from the serialized data.
        provided_tools: Tools provided by the user for decoding.

    Raises:
        IncompatibleToolsError: If provided tools don't include all serialized tools
            with matching schemas.
    """
    if not serialized_tools:
        return

    if provided_tools is None:
        missing_names = [t.name for t in serialized_tools]
        raise IncompatibleToolsError(
            f"Serialized data contains tools {missing_names} but no tools were provided",
        )

    if isinstance(provided_tools, Toolkit):
        tools_dict = provided_tools.tools_dict
    else:
        tools_dict = {tool.name: tool for tool in provided_tools}

    for serialized_tool in serialized_tools:
        tool_name = serialized_tool.name
        if tool_name not in tools_dict:
            raise IncompatibleToolsError(
                f"Serialized tool '{tool_name}' not found in provided tools",
            )

        provided_tool = tools_dict[tool_name]

        serialized_params = serialized_tool.parameters
        provided_params: dict[str, Any] = {
            "properties": provided_tool.parameters.properties,
            "required": provided_tool.parameters.required,
            "additionalProperties": provided_tool.parameters.additionalProperties,
        }
        if provided_tool.parameters.defs is not None:
            provided_params["defs"] = provided_tool.parameters.defs

        if serialized_params.properties != provided_params["properties"]:
            raise IncompatibleToolsError(
                f"Tool '{tool_name}' parameters properties mismatch",
            )
        if list(serialized_params.required) != provided_params["required"]:
            raise IncompatibleToolsError(
                f"Tool '{tool_name}' required parameters mismatch",
            )
        if (
            serialized_params.additionalProperties
            != provided_params["additionalProperties"]
        ):
            raise IncompatibleToolsError(
                f"Tool '{tool_name}' additionalProperties mismatch",
            )

        serialized_defs: dict[str, Any] | None = None
        if not isinstance(serialized_params.defs, msgspec.UnsetType):
            serialized_defs = serialized_params.defs
        provided_defs = provided_params.get("defs")
        if serialized_defs != provided_defs:
            raise IncompatibleToolsError(
                f"Tool '{tool_name}' $defs mismatch",
            )
        if serialized_tool.strict != provided_tool.strict:
            raise IncompatibleToolsError(
                f"Tool '{tool_name}' strict mode mismatch",
            )


def _validate_format_schema(
    serialized_format: SerializedFormat | None,
    provided_format: Format[FormattableT] | None,
) -> None:
    """Validate that provided format schema matches serialized format.

    Args:
        serialized_format: Format schema from the serialized data.
        provided_format: Format provided by the user for decoding.

    Raises:
        IncompatibleFormatError: If provided format schema doesn't match serialized format.
    """
    if serialized_format is None:
        return

    if provided_format is None:
        raise IncompatibleFormatError(
            f"Serialized data contains format '{serialized_format.name}' "
            "but no format was provided",
        )

    if serialized_format.schema != provided_format.schema:
        raise IncompatibleFormatError(
            f"Format schema mismatch: expected schema for '{serialized_format.name}'",
        )
