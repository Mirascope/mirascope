from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeAlias

from pydantic import BaseModel, Field

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
]


class CostMetadata(BaseModel):
    """Metadata required for accurate LLM API cost calculation across all providers."""

    # Common fields
    streaming_mode: bool | None = Field(
        None, description="Whether streaming API was used"
    )
    cached_response: bool | None = Field(
        None, description="Whether response was served from cache"
    )
    context_length: int | None = Field(
        None, description="Total context window length in tokens"
    )
    realtime_mode: bool | None = Field(
        None, description="Whether realtime processing was used"
    )
    region: str | None = Field(
        None, description="Cloud region for request (affects pricing in some providers)"
    )
    tier: str | None = Field(
        None, description="Service tier (e.g. standard, enterprise)"
    )

    # Media-related fields
    image_count: int | None = Field(None, description="Number of images in the request")
    audio_duration: float | None = Field(
        None, description="Duration of audio in seconds"
    )

    # OpenAI-specific fields
    vision_tokens: int | None = Field(
        None, description="[OpenAI] Number of vision tokens in the request"
    )
    audio_tokens: int | None = Field(
        None, description="[OpenAI] Number of audio tokens in the request"
    )
    realtime_tokens: int | None = Field(
        None, description="[OpenAI] Number of realtime tokens in the request"
    )

    # Anthropic-specific fields
    cache_write: bool | None = Field(
        None, description="[Anthropic] Whether cache write occurred"
    )
    tool_use_tokens: int | None = Field(
        None, description="[Anthropic] Tokens used for tool calls"
    )

    # Vertex/Google-specific fields
    character_count: int | None = Field(
        None,
        description="[Vertex/Google] Character count for character-based pricing models",
    )

    # Gemini-specific fields
    long_context_premium: bool | None = Field(
        None, description="[Gemini] Whether long context premium pricing applies"
    )
