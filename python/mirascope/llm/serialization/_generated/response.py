"""Serialization models generated from JSON Schema."""

from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar, Literal, TypeAlias

from msgspec import UNSET, Struct, UnsetType, field


class AssistantMessage(Struct, tag_field="role", tag="assistant"):
    role: ClassVar[Literal["assistant"]]
    content: list[AssistantContentPart]
    """Assistant message content parts"""

    name: str | None | UnsetType = UNSET
    """Optional assistant name"""

    provider: str | None | UnsetType = UNSET
    """Provider that generated this message"""

    model_id: str | None | UnsetType = UNSET
    """Model that generated this message"""

    raw_message: Any | UnsetType = UNSET
    """Provider-specific raw message representation"""


class AudioContent(Struct, tag_field="type", tag="audio"):
    type: ClassVar[Literal["audio"]]
    source: AudioSource


class Base64AudioSource(Struct):
    type: Literal["base64_audio_source"]
    data: str
    """Base64-encoded audio data"""

    mime_type: str
    """Audio MIME type (e.g., audio/wav)"""


class Base64DocumentSource(Struct, tag_field="type", tag="base64_document_source"):
    type: ClassVar[Literal["base64_document_source"]]
    data: str
    """Base64-encoded document data"""

    media_type: str
    """Document MIME type (e.g., application/pdf)"""


class Base64ImageSource(Struct, tag_field="type", tag="base64_image_source"):
    type: ClassVar[Literal["base64_image_source"]]
    data: str
    """Base64-encoded image data"""

    mime_type: str
    """Image MIME type (e.g., image/png)"""


class DocumentContent(Struct, tag_field="type", tag="document"):
    type: ClassVar[Literal["document"]]
    source: DocumentSource


class FinishReason(Enum):
    max_tokens = "max_tokens"
    refusal = "refusal"


class ImageContent(Struct, tag_field="type", tag="image"):
    type: ClassVar[Literal["image"]]
    source: ImageSource


class Metadata(Struct):
    serialized_at: str
    """ISO 8601 timestamp of serialization"""

    mirascope_version: str
    """Mirascope package version"""


class Mode(Enum):
    strict = "strict"
    json = "json"
    tool = "tool"


class SerializedFormat(Struct):
    name: str
    """Format name"""

    schema: dict[str, Any]
    """JSON Schema for the format"""

    mode: Mode
    """Formatting mode"""

    description: str | None | UnsetType = UNSET
    """Format description"""


class SerializedResponse(Struct):
    field_schema: str = field(name="$schema")
    """Schema identifier (e.g., mirascope/response/v1)"""

    version: str
    """Serialization format version (MAJOR.MINOR)"""

    type: Literal["response"]
    """Response type identifier"""

    provider: str
    """LLM provider name (e.g., anthropic, openai, google)"""

    model_id: str
    """Model identifier (e.g., claude-sonnet-4-20250514)"""

    messages: list[Message]
    """Message history including the assistant response"""

    metadata: Metadata
    """Serialization metadata"""

    finish_reason: FinishReason | None | UnsetType = UNSET
    """Reason for response completion, if not normal"""

    params: dict[str, Any] | None | UnsetType = UNSET
    """Request parameters used for generation"""

    tools: list[SerializedToolSchema] | None | UnsetType = UNSET
    """Tool schemas available for the response"""

    format: SerializedFormat | None | UnsetType = UNSET
    """Structured output format specification"""


class SerializedToolSchema(Struct):
    name: str
    """Tool name"""

    description: str
    """Tool description"""

    parameters: ToolParameterSchema
    strict: bool
    """Whether the tool uses strict mode"""


class SystemMessage(Struct, tag_field="role", tag="system"):
    role: ClassVar[Literal["system"]]
    content: list[TextContent]
    """System message content (single text)"""


class TextContent(Struct, tag_field="type", tag="text"):
    type: ClassVar[Literal["text"]]
    text: str
    """Text content"""


class TextDocumentSource(Struct, tag_field="type", tag="text_document_source"):
    type: ClassVar[Literal["text_document_source"]]
    data: str
    """Raw text content"""

    media_type: str
    """Document MIME type (e.g., text/plain)"""


class ThoughtContent(Struct, tag_field="type", tag="thought"):
    type: ClassVar[Literal["thought"]]
    thought: str
    """Model's thinking/reasoning content"""


class ToolCallContent(Struct, tag_field="type", tag="tool_call"):
    type: ClassVar[Literal["tool_call"]]
    id: str
    """Tool call identifier"""

    name: str
    """Tool name"""

    args: str | dict[str, Any]
    """Tool arguments (JSON string or object)"""


class ToolOutputContent(Struct, tag_field="type", tag="tool_output"):
    type: ClassVar[Literal["tool_output"]]
    id: str
    """Tool call identifier this output responds to"""

    name: str
    """Tool name"""

    value: Any
    """Tool execution result"""


class ToolParameterSchema(Struct):
    properties: dict[str, Any]
    """Parameter definitions"""

    required: list[str]
    """Required parameter names"""

    additionalProperties: bool
    defs: dict[str, Any] | UnsetType = UNSET
    """JSON Schema definitions for $ref"""


class URLDocumentSource(Struct, tag_field="type", tag="url_document_source"):
    type: ClassVar[Literal["url_document_source"]]
    url: str
    """Document URL"""


class URLImageSource(Struct, tag_field="type", tag="url_image_source"):
    type: ClassVar[Literal["url_image_source"]]
    url: str
    """Image URL"""


UserContentPart: TypeAlias = (
    TextContent | ImageContent | AudioContent | DocumentContent | ToolOutputContent
)


class UserMessage(Struct, tag_field="role", tag="user"):
    role: ClassVar[Literal["user"]]
    content: list[UserContentPart]
    """User message content parts"""

    name: str | None | UnsetType = UNSET
    """Optional user/session name"""


AssistantContentPart: TypeAlias = TextContent | ToolCallContent | ThoughtContent


AudioSource: TypeAlias = Base64AudioSource


DocumentSource: TypeAlias = (
    Base64DocumentSource | TextDocumentSource | URLDocumentSource
)


ImageSource: TypeAlias = Base64ImageSource | URLImageSource


Message: TypeAlias = SystemMessage | UserMessage | AssistantMessage
