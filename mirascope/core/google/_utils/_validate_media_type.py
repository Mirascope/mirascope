"""Utilities for validating supported media types for Google models."""


def _check_image_media_type(media_type: str) -> None:
    """Raises a `ValueError` if the image media type is not supported."""
    if media_type not in [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/heic",
        "image/heif",
    ]:
        raise ValueError(
            f"Unsupported image media type: {media_type}. "
            "Google currently only supports JPEG, PNG, WebP, HEIC, "
            "and HEIF images."
        )


def _check_audio_media_type(media_type: str) -> None:
    """Raises a `ValueError` if the audio media type is not supported."""
    if media_type not in [
        "audio/wav",
        "audio/mp3",
        "audio/aiff",
        "audio/aac",
        "audio/ogg",
        "audio/flac",
    ]:
        raise ValueError(
            f"Unsupported audio media type: {media_type}. "
            "Google currently only supports WAV, MP3, AIFF, AAC, OGG, "
            "and FLAC audio file types."
        )
