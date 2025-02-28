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


class VideoMetadata(BaseModel):
    """Metadata for a video for cost calculation"""

    duration_seconds: Annotated[
        float,
        Field(description="Duration of the video in seconds"),
    ]

    with_audio: Annotated[
        bool | None,
        Field(
            default=False,
            description="Whether the video includes audio that should be processed",
        ),
    ] = False

    tokens: Annotated[
        int | None,
        Field(default=None, description="Precalculated token count for this video"),
    ] = None


class AudioMetadata(BaseModel):
    """Metadata for an audio file for cost calculation"""

    duration_seconds: Annotated[
        float,
        Field(description="Duration of the audio in seconds"),
    ]

    with_timestamps: Annotated[
        bool | None,
        Field(default=False, description="Whether timestamps should be included"),
    ] = False

    tokens: Annotated[
        int | None,
        Field(default=None, description="Precalculated token count for this audio"),
    ] = None


class ImageMetadata(BaseModel):
    """Metadata for an image for cost calculation"""

    width: Annotated[
        int,
        Field(description="Width of the image in pixels"),
    ]

    height: Annotated[
        int,
        Field(description="Height of the image in pixels"),
    ]

    tokens: Annotated[
        int | None,
        Field(default=None, description="Precalculated token count for this image"),
    ] = None

    detail: Annotated[
        str | None,
        Field(default=None, description="Detail level of the image"),
    ] = None


class GoogleMetadata(BaseModel):
    """Google API specific metadata for cost calculation"""

    use_vertex_ai: Annotated[
        bool | None,
        Field(
            default=False,
            description="Whether to use Vertex AI pricing (vs. direct Gemini API)",
        ),
    ] = False

    grounding_requests: Annotated[
        int | None,
        Field(default=None, description="Number of Google Search grounding requests"),
    ] = None


class PDFImageMetadata(BaseModel):
    """Metadata for an image extracted from a PDF page"""

    width: Annotated[
        int,
        Field(description="Width of the image in pixels"),
    ]

    height: Annotated[
        int,
        Field(description="Height of the image in pixels"),
    ]

    tokens: Annotated[
        int | None,
        Field(default=None, description="Precalculated token count for this image"),
    ] = None


class PDFMetadata(BaseModel):
    """Metadata specific to PDF documents for cost calculation"""

    page_count: Annotated[
        int | None,
        Field(default=None, description="Number of pages in the PDF"),
    ] = None

    text_tokens: Annotated[
        int | None,
        Field(
            default=None, description="Number of tokens from text content in the PDF"
        ),
    ] = None

    images: Annotated[
        list[PDFImageMetadata] | None,
        Field(
            default=None,
            description="List of images extracted from PDF with width and height information",
        ),
    ] = None

    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="Whether this PDF was cached for reduced token costs",
        ),
    ] = None


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
    batch_mode: Annotated[
        bool | None,
        Field(
            default=False,
            description="Whether batch mode is used (discount usually applies)",
        ),
    ] = None

    # Media-related fields
    images: Annotated[
        list[ImageMetadata] | None,
        Field(default=None, description="List of images with their metadata"),
    ] = None
    videos: Annotated[
        list[VideoMetadata] | None,
        Field(default=None, description="List of videos with their metadata"),
    ] = None
    audio: Annotated[
        list[AudioMetadata] | None,
        Field(default=None, description="List of audio clips with their metadata"),
    ] = None
    audio_output: Annotated[
        list[AudioMetadata] | None,
        Field(
            default=None, description="List of audio output clips with their metadata"
        ),
    ] = None
    # PDF-related fields
    pdf: Annotated[
        PDFMetadata | None,
        Field(default=None, description="Metadata for PDF documents"),
    ] = None

    # Context caching related fields
    context_cache_tokens: Annotated[
        int | None,
        Field(default=None, description="Number of cached context tokens"),
    ] = None
    context_cache_hours: Annotated[
        float | None,
        Field(default=None, description="Number of hours to keep context in cache"),
    ] = None

    # Provider-specific fields
    google: Annotated[
        GoogleMetadata | None,
        Field(
            default=None,
            description="Google/Gemini-specific metadata for cost calculation",
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

    # If the provider happens to provide the cost, we should just use that.
    cost: Annotated[
        float | None,
        Field(default=None, description="Cost provided by the API response"),
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
