"""The `Video` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Video:
    """Video content for a message.

    Video can be included in messages for video-based interactions.
    """

    type: Literal["video"] = "video"

    id: str | None
    """A unique identifier for this video content. This is useful for tracking and referencing generated videos."""

    data: str | bytes
    """The video data, which can be a URL, file path, base64-encoded string, or binary data."""

    transcript: str | None
    """The transcript of the video, if available. This is useful for accessibility and search."""

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
