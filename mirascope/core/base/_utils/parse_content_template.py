"""This module provides a function to parse content parts from a prompt template."""

import re
import urllib.request
from typing import Any, List, Literal, cast, get_args

from typing_extensions import TypedDict

from ..message_param import (
    AudioPart,
    BaseMessageParam,
    ImagePart,
    TextPart,
    _Detail,
)
from .format_template import format_template

_PartType = Literal["text", "image", "images", "audio", "audios"]


class _Part(TypedDict):
    template: str
    type: _PartType


class _ImageOptions(TypedDict, total=False):
    detail: _Detail


def _parse_parts(template: str) -> List[_Part]:
    # \{ and \} match the literal curly braces.
    #
    # ([^:{}]+) captures one or more characters that are not : or { or }.
    # This captures the type (e.g., "image" or "audio").
    #
    # : matches the literal colon separating the type from the content.
    #
    # ([^{}]+) captures one or more characters that are not { or }.
    # This captures the content after the colon.
    pattern = r"\{([^:{}]+):([^{}]+)\}"
    split = re.split(pattern, template)
    parts: List[_Part] = []
    for i in range(0, len(split), 3):
        if split[i]:
            parts.append(_Part(template=split[i], type="text"))
        if i + 2 < len(split):
            special_type = split[i + 1]
            if special_type not in list(get_args(_PartType)):
                raise ValueError(f"Template type '{special_type}' not supported.")
            special_type = cast(_PartType, special_type)
            special_content = split[i + 2]
            parts.append(
                _Part(
                    template=f"{{{special_type}:{special_content}}}", type=special_type
                )
            )
    return parts


def _get_image_type(image_data: bytes) -> str:
    if image_data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    elif image_data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    elif image_data.startswith(b"GIF87a") or image_data.startswith(b"GIF89a"):
        return "gif"
    elif image_data.startswith(b"RIFF") and image_data[8:12] == b"WEBP":
        return "webp"
    elif image_data[4:12] in (
        b"ftypmif1",
        b"ftypmsf1",
        b"ftypheic",
        b"ftypheix",
        b"ftyphevc",
        b"ftyphevx",
    ):
        # HEIF and HEIC files start with 'ftyp' followed by specific codes
        if image_data[4:8] == b"ftyp":
            subtype = image_data[8:12]
            if subtype in (b"heic", b"heix"):
                return "heic"
            elif subtype in (b"mif1", b"msf1", b"hevc", b"hevx"):
                return "heif"
    raise ValueError("Unsupported image type")


def _load_image(source: str | bytes) -> tuple[str, bytes]:
    try:
        # Some typing weirdness here where checking `isinstance(source, bytes)` results
        # in a type hint of `str | bytearray | memoryview` for source in the else.
        if isinstance(source, (bytes, bytearray, memoryview)):
            image_data = source
        elif source.startswith(("http://", "https://")):
            with urllib.request.urlopen(source) as response:
                image_data = response.read()
        else:
            with open(source, "rb") as f:
                image_data = f.read()
        image_type = f"image/{_get_image_type(image_data)}"
        return image_type, image_data
    except Exception as e:
        raise ValueError(f"Failed to load or encode image from {source}: {str(e)}")


def _parse_image_options(options_str: str) -> _ImageOptions:
    options: _ImageOptions = {}
    for option in options_str.split(","):
        if not option:
            continue
        key, value = option.split(":")
        if key == "detail":
            if value not in list(get_args(_Detail)):
                raise ValueError(f"Invalid detail value: {value}")
            value = cast(_Detail, value)
            options["detail"] = value
    return options


def _construct_image_part(source: str, options: list[str]) -> ImagePart:
    options_dict = _parse_image_options(",".join(options))
    media_type, image = _load_image(source)
    return {
        "type": "image",
        "media_type": media_type,
        "image": image,
        "detail": options_dict.get("detail"),
    }


def _get_audio_type(audio_data: bytes) -> str:
    if audio_data.startswith(b"RIFF") and audio_data[8:12] == b"WAVE":
        return "wav"
    elif audio_data.startswith(b"ID3") or audio_data.startswith(b"\xff\xfb"):
        return "mp3"
    elif audio_data.startswith(b"FORM") and audio_data[8:12] == b"AIFF":
        return "aiff"
    elif audio_data.startswith(b"\xff\xf1") or audio_data.startswith(b"\xff\xf9"):
        return "aac"
    elif audio_data.startswith(b"OggS"):
        return "ogg"
    elif audio_data.startswith(b"fLaC"):
        return "flac"

    raise ValueError("Unsupported file type")


def _load_audio(source: str | bytes) -> tuple[str, bytes]:
    try:
        # See comment in _load_image for explanation of this typing weirdness.
        if isinstance(source, (bytes, bytearray, memoryview)):
            audio_data = source
        elif source.startswith(("http://", "https://")):
            with urllib.request.urlopen(source) as response:
                audio_data = response.read()
        else:
            with open(source, "rb") as f:
                audio_data = f.read()

        audio_type = f"audio/{_get_audio_type(audio_data)}"
        return audio_type, audio_data
    except Exception as e:
        raise ValueError(f"Failed to load or encode audio from {source}: {str(e)}")


def _construct_audio_part(source: str) -> AudioPart:
    # Note: audio does not currently support additional options, at least for now.
    media_type, audio = _load_audio(source)
    return {"type": "audio", "media_type": media_type, "audio": audio}


def _construct_parts(
    part: _Part, attrs: dict[str, Any]
) -> List[TextPart | ImagePart | AudioPart]:
    if part["type"] == "text":
        return [{"type": "text", "text": format_template(part["template"], attrs)}]
    elif part["type"] == "image":
        path_key, *options = part["template"][7:-1].split(",")
        source = attrs[path_key]
        return [_construct_image_part(attrs[path_key], options)] if source else []
    elif part["type"] == "images":
        path_key, *options = part["template"][8:-1].split(",")
        sources = attrs[path_key]
        if not isinstance(sources, list):
            raise ValueError(
                f"When using 'images' template, '{path_key}' must be a list."
            )
        return (
            [_construct_image_part(source, options) for source in sources]
            if sources
            else []
        )
    elif part["type"] == "audio":
        path_key = part["template"][7:-1]
        source = attrs[path_key]
        return [_construct_audio_part(source)] if source else []
    elif part["type"] == "audios":
        path_key = part["template"][8:-1]
        sources = attrs[path_key]
        if not isinstance(sources, list):
            raise ValueError(
                f"When using 'audios' template, '{path_key}' must be a list."
            )
        return [_construct_audio_part(source) for source in sources] if sources else []
    raise ValueError(f"Template type '{part['type']}' not supported.")


def parse_content_template(
    role: str, template: str, attrs: dict[str, Any]
) -> BaseMessageParam | None:
    """Returns the content template parsed and formatted as a message parameter."""
    if not template:
        return None

    parts = _parse_parts(template)
    content = [item for part in parts for item in _construct_parts(part, attrs)]
    return {"role": role, "content": content}
