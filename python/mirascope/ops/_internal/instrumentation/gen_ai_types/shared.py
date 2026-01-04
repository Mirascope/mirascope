"""OpenTelemetry Gen AI Semantic Conventions types."""

from __future__ import annotations

from typing import Any, Literal, TypeAlias, TypedDict
from typing_extensions import NotRequired


class BlobPart(TypedDict):
    type: Literal["blob"]
    """The type of the content captured in this part."""

    mime_type: NotRequired[str | None]
    """The IANA MIME type of the attached data."""

    modality: Modality | str
    """The general modality of the data if it is known. Instrumentations SHOULD also set the mimeType field if the specific type is known."""

    content: str
    """Raw bytes of the attached data. This field SHOULD be encoded as a base64 string when transmitted as JSON."""


class FilePart(TypedDict):
    type: Literal["file"]
    """The type of the content captured in this part."""

    mime_type: NotRequired[str | None]
    """The IANA MIME type of the attached data."""

    modality: Modality | str
    """The general modality of the data if it is known. Instrumentations SHOULD also set the mimeType field if the specific type is known."""

    file_id: str
    """An identifier referencing a file that was pre-uploaded to the provider."""


class GenericPart(TypedDict):
    type: str
    """The type of the content captured in this part."""


Modality: TypeAlias = Literal["image", "video", "audio"]


class ReasoningPart(TypedDict):
    type: Literal["reasoning"]
    """The type of the content captured in this part."""

    content: str
    """Reasoning/thinking content received from the model."""


Role: TypeAlias = Literal["system", "user", "assistant", "tool"]


class TextPart(TypedDict):
    type: Literal["text"]
    """The type of the content captured in this part."""

    content: str
    """Text content sent to or received from the model."""


class ToolCallRequestPart(TypedDict):
    type: Literal["tool_call"]
    """The type of the content captured in this part."""

    id: NotRequired[str | None]
    """Unique identifier for the tool call."""

    name: str
    """Name of the tool."""

    arguments: NotRequired[Any]
    """Arguments for the tool call."""


class ToolCallResponsePart(TypedDict):
    type: Literal["tool_call_response"]
    """The type of the content captured in this part."""

    id: NotRequired[str | None]
    """Unique tool call identifier."""

    response: Any
    """Tool call response."""


class UriPart(TypedDict):
    type: Literal["uri"]
    """The type of the content captured in this part."""

    mime_type: NotRequired[str | None]
    """The IANA MIME type of the attached data."""

    modality: Modality | str
    """The general modality of the data if it is known. Instrumentations SHOULD also set the mimeType field if the specific type is known."""

    uri: str
    """A URI referencing attached data. It should not be a base64 data URL, which should use the `blob` part instead. The URI may use a scheme known to the provider api (e.g. `gs://bucket/object.png`), or be a publicly accessible location."""
