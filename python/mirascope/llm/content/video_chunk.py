"""The `VideoChunk` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class VideoChunk:
    """Video output content when retrieved through a stream."""

    type: Literal["video_chunk"] = "video_chunk"

    mime_type: Literal[
        "video/mp4",
        "video/mpeg",
        "video/mov",
        "video/avi",
        "video/x-flv",
        "video/mpg",
        "video/webm",
        "video/wmv",
        "video/3gpp",
    ]
    """The MIME type of the video, e.g., 'video/mp4', 'video/webm'."""

    id: str | None = None
    """A unique identifier for this series of chunks, if available."""

    partial: bytes
    """The accumulated video data in this chunk."""
