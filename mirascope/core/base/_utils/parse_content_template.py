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
from .get_audio_type import get_audio_type
from .get_image_type import get_image_type

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
            special_type = cast(_PartType, special_type)  # type: ignore
            special_content = split[i + 2]
            parts.append(
                _Part(
                    template=f"{{{special_type}:{special_content}}}", type=special_type
                )
            )
    return parts


def _load_media(source: str | bytes) -> bytes:
    try:
        # Some typing weirdness here where checking `isinstance(source, bytes)` results
        # in a type hint of `str | bytearray | memoryview` for source in the else.
        if isinstance(source, (bytes, bytearray, memoryview)):
            data = source
        elif source.startswith(("http://", "https://")):
            with urllib.request.urlopen(source) as response:
                data = response.read()
        else:
            with open(source, "rb") as f:
                data = f.read()
        return data
    except Exception as e:  # pragma: no cover
        raise ValueError(
            f"Failed to load or encode data from {source}: {str(e)}"
        )  # pragma: no cover


def _parse_image_options(options_str: str) -> _ImageOptions:
    options: _ImageOptions = {}
    for option in options_str.split(","):
        if not option:
            continue
        key, value = option.split(":")
        if key == "detail":
            if value not in list(get_args(_Detail)):
                raise ValueError(f"Invalid detail value: {value}")
            value = cast(_Detail, value)  # type: ignore
            options["detail"] = value
    return options


def _construct_image_part(source: str | bytes, options: list[str]) -> ImagePart:
    options_dict = _parse_image_options(",".join(options))
    image = _load_media(source)
    return {
        "type": "image",
        "media_type": f"image/{get_image_type(image)}",
        "image": image,
        "detail": options_dict.get("detail"),
    }


def _construct_audio_part(source: str | bytes) -> AudioPart:
    # Note: audio does not currently support additional options, at least for now.
    audio = _load_media(source)
    return {
        "type": "audio",
        "media_type": f"audio/{get_audio_type(audio)}",
        "audio": audio,
    }


def _construct_parts(
    part: _Part, attrs: dict[str, Any]
) -> List[TextPart | ImagePart | AudioPart]:
    if part["type"] == "image":
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
    else:  # text type
        return [{"type": "text", "text": format_template(part["template"], attrs)}]


def parse_content_template(
    role: str, template: str, attrs: dict[str, Any]
) -> BaseMessageParam | None:
    """Returns the content template parsed and formatted as a message parameter."""
    if not template:
        return None

    parts = _parse_parts(template)
    content = [item for part in parts for item in _construct_parts(part, attrs)]
    return {"role": role, "content": content}
