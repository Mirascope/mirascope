"""This module provides a function to parse content parts from a prompt template."""

import imghdr
import re
import urllib.request
from typing import Any, List, cast, get_args

from typing_extensions import TypedDict

from ..message_param import BaseMessageParam, ImagePart, TextPart, _Detail, _PartType
from .format_template import format_template


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


def _load_and_encode_image(source: str) -> tuple[str, bytes]:
    try:
        if source.startswith(("http://", "https://")):
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
    media_type, image = _load_and_encode_image(source)
    return {
        "type": "image",
        "media_type": media_type,
        "image": image,
        "detail": options_dict.get("detail"),
    }


def _construct_parts(part: _Part, attrs: dict[str, Any]) -> List[TextPart | ImagePart]:
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
