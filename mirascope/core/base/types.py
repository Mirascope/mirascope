from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from PIL import Image
    from pydub import AudioSegment

    has_pil_module: bool
    has_pydub_module: bool
else:
    try:
        from PIL import Image  # pyright: ignore [reportAssignmentType]

        has_pil_module = True
    except ImportError:  # pragma: no cover
        has_pil_module = False

        class Image:
            class Image:
                def tobytes(self) -> bytes: ...

    try:
        from pydub import AudioSegment  # pyright: ignore [reportAssignmentType]

        has_pydub_module = True
    except ImportError:  # pragma: no cover
        has_pydub_module = False

        from io import FileIO

        class AudioSegment:
            def set_frame_rate(self, rate: int) -> AudioSegment: ...
            def set_channels(self, channels: int) -> AudioSegment: ...
            def set_sample_width(self, sample_width: int) -> AudioSegment: ...
            def export(self, format: str) -> FileIO: ...
            def read(self) -> bytes: ...


FinishReason: TypeAlias = Literal["stop", "length", "tool_calls", "content_filter"]


class Usage(BaseModel):
    input_tokens: int
    """Number of tokens in the prompt."""

    cached_tokens: int
    """Number of tokens used that were previously cached (and thus cheaper)."""

    output_tokens: int
    """Number of tokens in the generated output."""

    total_tokens: int
    """Total number of tokens used in the request (prompt + completion)."""


JsonableType: TypeAlias = (
    str
    | int
    | float
    | bool
    | bytes
    | list["JsonableType"]
    | set["JsonableType"]
    | tuple["JsonableType", ...]
    | dict[str, "JsonableType"]
    | BaseModel
)

try:
    from litellm import (
        ModelResponse as LitellmModelResponse,  # pyright: ignore [reportPrivateImportUsage, reportAssignmentType]
    )
except ImportError:  # pragma: no cover

    class LitellmModelResponse: ...


class CostMetadata(BaseModel):
    """Metadata required for accurate LLM API cost calculation across all providers."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Common fields
    input_tokens: Annotated[
        int | float | None,
        Field(default=None, description="Input tokens"),
    ] = None
    output_tokens: Annotated[
        int | float | None,
        Field(default=None, description="Output tokens"),
    ] = None
    cached_tokens: Annotated[
        int | float | None,
        Field(default=None, description="Cached tokens"),
    ] = None
    streaming_mode: Annotated[
        bool | None,
        Field(default=None, description="Whether streaming API was used"),
    ] = None
    cached_response: Annotated[
        bool | None,
        Field(default=None, description="Whether response was served from cache"),
    ] = None
    context_length: Annotated[
        int | None,
        Field(default=None, description="Total context window length in tokens"),
    ] = None
    realtime_mode: Annotated[
        bool | None,
        Field(default=None, description="Whether realtime processing was used"),
    ] = None
    region: Annotated[
        str | None,
        Field(
            default=None,
            description="Cloud region for request (affects pricing in some providers)",
        ),
    ] = None
    tier: Annotated[
        str | None,
        Field(default=None, description="Service tier (e.g. standard, enterprise)"),
    ] = None

    # Media-related fields
    image_count: Annotated[
        int | None,
        Field(default=None, description="Number of images in the request"),
    ] = None
    audio_duration: Annotated[
        float | None, Field(default=None, description="Duration of audio in seconds")
    ] = None

    # OpenAI-specific fields
    vision_tokens: Annotated[
        int | None,
        Field(
            default=None, description="[OpenAI] Number of vision tokens in the request"
        ),
    ] = None
    audio_tokens: Annotated[
        int | None,
        Field(
            default=None, description="[OpenAI] Number of audio tokens in the request"
        ),
    ] = None
    realtime_tokens: Annotated[
        int | None,
        Field(
            default=None,
            description="[OpenAI] Number of realtime tokens in the request",
        ),
    ] = None

    # Anthropic-specific fields
    cache_write: Annotated[
        bool | None,
        Field(default=None, description="[Anthropic] Whether cache write occurred"),
    ] = None
    tool_use_tokens: Annotated[
        int | None,
        Field(default=None, description="[Anthropic] Tokens used for tool calls"),
    ] = None

    # LiteLLM-specific fields
    litellm_response: Annotated[
        LitellmModelResponse | None,
        Field(default=None, description="[Litellm] Response from API"),
    ] = None


Provider: TypeAlias = Literal[
    "anthropic",
    "azure",
    "bedrock",
    "cohere",
    "gemini",
    "google",
    "groq",
    "litellm",
    "mistral",
    "openai",
    "vertex",
    "xai",
]
LocalProvider: TypeAlias = Literal[
    "ollama",
    "vllm",
]
