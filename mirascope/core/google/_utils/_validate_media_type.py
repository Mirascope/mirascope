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


def _check_document_media_type(media_type: str) -> None:
    """Raises a `ValueError` if the document media type is not supported."""

    if media_type not in [
        "application/pdf",
        "application/x-javascript",
        "text/javascript",
        "application/x-python",
        "text/x-python",
        "text/plain",
        "text/html",
        "text/css",
        "text/csv",
        "text/xml",
        "text/rtf",
        "text/md",
    ]:
        raise ValueError(
            f"Unsupported document media type: {media_type}. "
            "Google currently only supports PDF, JavaScript, Python, TXT, HTML, CSS, "
            "CSV, XML, RTF, and Markdown document types."
        )
