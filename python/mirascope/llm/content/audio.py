"""The `Audio` content class."""

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, get_args

import httpx

AudioMimeType = Literal[
    "audio/wav",
    "audio/mp3",
    "audio/aiff",
    "audio/aac",
    "audio/ogg",
    "audio/flac",
]  # TODO: add e2e tests for every supported type

MIME_TYPES = get_args(AudioMimeType)

# Maximum audio size in bytes (25MB)
MAX_AUDIO_SIZE = 25 * 1024 * 1024


def infer_audio_type(audio_data: bytes) -> AudioMimeType:
    """Get the MIME type of an audio file from its raw bytes.

    Raises:
        ValueError: If the audio type cannot be determined or data is too small
    """
    if len(audio_data) < 12:
        raise ValueError("Audio data too small to determine type (minimum 12 bytes)")

    if audio_data.startswith(b"RIFF") and audio_data[8:12] == b"WAVE":
        return "audio/wav"
    elif audio_data.startswith(b"ID3") or audio_data.startswith(b"\xff\xfb"):
        return "audio/mp3"
    elif audio_data.startswith(b"FORM") and audio_data[8:12] == b"AIFF":
        return "audio/aiff"
    elif audio_data.startswith(b"\xff\xf1") or audio_data.startswith(b"\xff\xf9"):
        return "audio/aac"
    elif audio_data.startswith(b"OggS"):
        return "audio/ogg"
    elif audio_data.startswith(b"fLaC"):
        return "audio/flac"
    raise ValueError("Unsupported audio type")


@dataclass(kw_only=True)
class Base64AudioSource:
    """Audio data represented as a base64 encoded string."""

    type: Literal["base64_audio_source"]

    data: str
    """The audio data, as a base64 encoded string."""

    mime_type: AudioMimeType
    """The mime type of the audio (e.g. audio/mp3)."""


def _process_audio_bytes(data: bytes, max_size: int) -> Base64AudioSource:
    """Validate and process audio bytes into a Base64AudioSource.

    Args:
        data: Raw audio bytes
        max_size: Maximum allowed size in bytes

    Returns:
        A Base64AudioSource with validated and encoded data

    Raises:
        ValueError: If data size exceeds max_size
    """
    size = len(data)
    if size > max_size:
        raise ValueError(
            f"Audio size ({size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        )

    mime_type = infer_audio_type(data)
    encoded_data = base64.b64encode(data).decode("utf-8")
    return Base64AudioSource(
        type="base64_audio_source",
        data=encoded_data,
        mime_type=mime_type,
    )


@dataclass(kw_only=True)
class Audio:
    """Audio content for a message.

    Audio can be included in messages for voice or sound-based interactions.
    """

    type: Literal["audio"] = "audio"

    source: Base64AudioSource

    @classmethod
    def download(cls, url: str, *, max_size: int = MAX_AUDIO_SIZE) -> "Audio":
        """Download and encode an audio file from a URL.

        Args:
            url: The URL of the audio file to download
            max_size: Maximum allowed audio size in bytes (default: 25MB)

        Returns:
            An `Audio` with a `Base64AudioSource`

        Raises:
            ValueError: If the downloaded audio exceeds max_size
        """
        response = httpx.get(url, follow_redirects=True)
        response.raise_for_status()
        return cls(source=_process_audio_bytes(response.content, max_size))

    @classmethod
    async def download_async(
        cls, url: str, *, max_size: int = MAX_AUDIO_SIZE
    ) -> "Audio":
        """Asynchronously download and encode an audio file from a URL.

        Args:
            url: The URL of the audio file to download
            max_size: Maximum allowed audio size in bytes (default: 25MB)

        Returns:
            An `Audio` with a `Base64AudioSource`

        Raises:
            ValueError: If the downloaded audio exceeds max_size
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return cls(source=_process_audio_bytes(response.content, max_size))

    @classmethod
    def from_file(cls, file_path: str, *, max_size: int = MAX_AUDIO_SIZE) -> "Audio":
        """Create an `Audio` from a file path.

        Args:
            file_path: Path to the audio file
            max_size: Maximum allowed audio size in bytes (default: 25MB)

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file size exceeds max_size
        """
        path = Path(file_path)
        file_size = path.stat().st_size
        if file_size > max_size:
            raise ValueError(
                f"Audio file size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
            )
        with open(path, "rb") as f:
            audio_bytes = f.read()
        return cls(source=_process_audio_bytes(audio_bytes, max_size))

    @classmethod
    def from_bytes(cls, data: bytes, *, max_size: int = MAX_AUDIO_SIZE) -> "Audio":
        """Create an `Audio` from raw bytes.

        Args:
            data: Raw audio bytes
            max_size: Maximum allowed audio size in bytes (default: 25MB)

        Raises:
            ValueError: If the data size exceeds max_size
        """
        return cls(source=_process_audio_bytes(data, max_size))
