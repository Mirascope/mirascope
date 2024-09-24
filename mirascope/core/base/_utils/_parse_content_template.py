"""This module provides a function to parse content parts from a prompt template."""

import re
import urllib.request
from typing import Any, Literal, cast

from typing_extensions import TypedDict

from ..message_param import (
    AudioPart,
    BaseMessageParam,
    CacheControlPart,
    ImagePart,
    TextPart,
)
from ._format_template import format_template
from ._get_audio_type import get_audio_type
from ._get_image_type import get_image_type

_PartType = Literal["text", "image", "images", "audio", "audios", "cache_control"]


class _Part(TypedDict):
    template: str
    type: _PartType
    options: dict[str, str] | None


def _parse_parts(template: str) -> list[_Part]:
    # \{ and \} match the literal curly braces.
    #
    # ([^:{}]*) captures content before the colon that are not { or } or :.
    # This can be empty when using `cache_control`.
    #
    # : matches the literal colon separating the type from the content.
    #
    # (image|images|...) captures the supported special type after the colon.
    #
    # (?:\(([^)]*)\))? captures the optional additional options in parentheses.
    pattern = r"\{([^:{}]*):(image|images|audio|audios|cache_control)(?:\(([^)]*)\))?\}"
    split = re.split(pattern, template)
    parts: list[_Part] = []
    for i in range(0, len(split), 4):
        if split[i]:
            parts.append(_Part(template=split[i], type="text", options=None))
        if i + 3 < len(split):
            special_content = split[i + 1]
            special_type = cast(_PartType, split[i + 2])
            special_options = split[i + 3]
            if special_options is not None:
                options: dict[str, str] = {}
                for option in special_options.split(","):
                    key, value = option.split("=")
                    options[key] = value
                special_options = options
            parts.append(
                _Part(
                    template=special_content, type=special_type, options=special_options
                )
            )
    return parts


def _load_media(source: str | bytes) -> bytes:
    try:
        # Some typing weirdness here where checking `isinstance(source, bytes)` results
        # in a type hint of `str | bytearray | memoryview` for source in the else.
        if isinstance(source, bytes | bytearray | memoryview):
            data = source
        elif source.startswith(("http://", "https://", "data:", "file://")):
            with urllib.request.urlopen(source) as response:
                data = response.read()
        else:
            with open(source, "rb") as f:
                data = f.read()
        return data
    except Exception as e:  # pragma: no cover
        raise ValueError(
            f"Failed to load or encode data from {source}"
        ) from e  # pragma: no cover


def _construct_image_part(
    source: str | bytes, options: dict[str, str] | None
) -> ImagePart:
    image = _load_media(source)
    detail = None
    if options:
        detail = options.get("detail", None)
    return ImagePart(
        type="image",
        media_type=f"image/{get_image_type(image)}",
        image=image,
        detail=detail,
    )


def _construct_audio_part(source: str | bytes) -> AudioPart:
    # Note: audio does not currently support additional options, at least for now.
    audio = _load_media(source)
    return AudioPart(
        type="audio", media_type=f"audio/{get_audio_type(audio)}", audio=audio
    )


def _construct_parts(
    part: _Part, attrs: dict[str, Any]
) -> list[TextPart] | list[ImagePart] | list[AudioPart] | list[CacheControlPart]:
    if part["type"] == "image":
        source = attrs[part["template"]]
        return [_construct_image_part(source, part["options"])] if source else []
    elif part["type"] == "images":
        sources = attrs[part["template"]]
        if not isinstance(sources, list):
            raise ValueError(
                f"When using 'images' template, '{part['template']}' must be a list."
            )
        return (
            [_construct_image_part(source, part["options"]) for source in sources]
            if sources
            else []
        )
    elif part["type"] == "audio":
        source = attrs[part["template"]]
        return [_construct_audio_part(source)] if source else []
    elif part["type"] == "audios":
        sources = attrs[part["template"]]
        if not isinstance(sources, list):
            raise ValueError(
                f"When using 'audios' template, '{part['template']}' must be a list."
            )
        return [_construct_audio_part(source) for source in sources] if sources else []
    elif part["type"] == "cache_control":
        return [
            CacheControlPart(
                type="cache_control",
                cache_type=part["options"].get("type", "ephemeral")
                if part["options"]
                else "ephemeral",
            )
        ]
    else:  # text type
        formatted_template = format_template(part["template"].strip(), attrs)
        if not formatted_template:
            return []
        return [TextPart(type="text", text=formatted_template)]


def parse_content_template(
    role: str, template: str, attrs: dict[str, Any]
) -> BaseMessageParam | None:
    """Returns the content template parsed and formatted as a message parameter."""
    if not template:
        return None

    parts = [
        item
        for part in _parse_parts(template)
        for item in _construct_parts(part, attrs)
    ]

    if not parts:
        return None

    if len(parts) == 1 and parts[0].type == "text":
        return BaseMessageParam(role=role, content=parts[0].text)
    return BaseMessageParam(role=role, content=parts)
