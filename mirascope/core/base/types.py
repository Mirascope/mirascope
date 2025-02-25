from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeAlias

from pydantic import BaseModel
from typing_extensions import TypedDict

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


class CostMetadata(TypedDict, total=False):
    """Metadata related to cost calculation for LLM API calls."""

    streaming_mode: bool | None  # Whether streaming API was used
    cached_response: bool | None  # Whether response was from cache
    image_count: int | None  # Number of images in the request
    audio_duration: float | None  # Duration of audio in seconds
    context_length: int | None  # Total context window length
    realtime_mode: bool | None  # Whether realtime processing was used
    region: str | None  # Cloud region for request
    tier: str | None  # Service tier (e.g. standard, enterprise)
