"""This module provides a function to parse content parts from a prompt template."""

import re
import urllib.request
from functools import reduce
from typing import Any, Literal, cast

from typing_extensions import TypedDict

from ..message_param import (
    AudioPart,
    AudioURLPart,
    BaseMessageParam,
    CacheControlPart,
    DocumentPart,
    ImagePart,
    ImageURLPart,
    TextPart,
)
from ..types import Image, has_pil_module
from ._format_template import format_template
from ._get_audio_type import get_audio_type
from ._get_document_type import get_document_type
from ._get_image_type import get_image_type
from ._pil_image_to_bytes import pil_image_to_bytes

_PartType = Literal[
    "image",
    "images",
    "audio",
    "audios",
    "text",
    "texts",
    "document",
    "documents",
    "cache_control",
    "part",
    "parts",
]


class _Part(TypedDict):
    template: str
    type: _PartType
    options: dict[str, str] | None


def _cleanup_text_preserve_newlines(text: str) -> str:
    def clean_line(line: str) -> str:
        # Remove '\r' to handle Windows-style line breaks
        line = line.replace("\r", "")

        # Remove zero-width spaces (common examples)
        zero_width_spaces = ["\u200b", "\u200c", "\u200d", "\ufeff"]
        for zw in zero_width_spaces:
            line = line.replace(zw, "")

        # Remove all fullwidth spaces (u3000) anywhere in the line
        line = line.replace("\u3000", "")

        # Strip leading/trailing half-width spaces (but keep tabs/newlines)
        line = line.strip(" ")

        # Remove leading tabs
        line = line.lstrip("\t")
        # Remove trailing tabs
        line = line.rstrip("\t")

        return line

    # Split lines but preserve the newline at the end of each line
    lines = text.splitlines(keepends=True)

    # Use `map` to apply `clean_line` to each line
    cleaned_lines = map(clean_line, lines)

    # Use `reduce` to concatenate all lines into a single string
    return reduce(lambda acc, x: acc + x, cleaned_lines, "")


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
    pattern = r"\{([^:{}]*):(image|images|audio|audios|document|documents|text|texts|cache_control|part|parts)(?:\(([^)]*)\))?\}"
    split = re.split(pattern, template)
    parts: list[_Part] = []
    for i in range(0, len(split), 4):
        if split[i]:
            parts.append(
                _Part(
                    template=_cleanup_text_preserve_newlines(split[i]),
                    type="text",
                    options=None,
                )
            )
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
    source: str | bytes | Image.Image, options: dict[str, str] | None
) -> ImagePart | ImageURLPart:
    detail = None
    if options:
        detail = options.get("detail", None)
    if isinstance(source, str) and source.startswith(("http://", "https://", "gs://")):
        return ImageURLPart(type="image_url", url=source, detail=detail)
    if isinstance(source, Image.Image):
        image = pil_image_to_bytes(source)
        media_type = (
            Image.MIME[source.format]
            if has_pil_module and source.format
            else "image/unknown"
        )
    else:
        image = _load_media(source)
        media_type = f"image/{get_image_type(image)}"
    return ImagePart(
        type="image",
        media_type=media_type,
        image=image,
        detail=detail,
    )


def _construct_audio_part(source: str | bytes) -> AudioPart | AudioURLPart:
    # Note: audio does not currently support additional options, at least for now.
    if isinstance(source, str) and source.startswith(("http://", "https://", "gs://")):
        return AudioURLPart(type="audio_url", url=source)
    audio = _load_media(source)
    return AudioPart(
        type="audio", media_type=f"audio/{get_audio_type(audio)}", audio=audio
    )


def _construct_document_part(source: str | bytes) -> DocumentPart:
    document = _load_media(source)
    return DocumentPart(
        type="document",
        media_type=f"application/{get_document_type(document)}",
        document=document,
    )


def _construct_parts(
    part: _Part, attrs: dict[str, Any]
) -> list[
    TextPart
    | ImagePart
    | ImageURLPart
    | AudioPart
    | AudioURLPart
    | CacheControlPart
    | DocumentPart
]:
    if part["type"] in "image":
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
    elif part["type"] == "document":
        source = attrs[part["template"]]
        return [_construct_document_part(source)] if source else []
    elif part["type"] == "documents":
        sources = attrs[part["template"]]
        if not isinstance(sources, list):
            raise ValueError(
                f"When using 'documents' template, '{part['template']}' must be a list."
            )
        return (
            [_construct_document_part(source) for source in sources] if sources else []
        )
    elif part["type"] == "cache_control":
        return [
            CacheControlPart(
                type="cache_control",
                cache_type=part["options"].get("type", "ephemeral")
                if part["options"]
                else "ephemeral",
            )
        ]
    elif part["type"] == "part":
        source = attrs[part["template"]]
        if not isinstance(
            source,
            TextPart
            | ImagePart
            | ImageURLPart
            | AudioPart
            | AudioURLPart
            | CacheControlPart
            | DocumentPart,
        ):
            raise ValueError(
                f"When using 'part' template, '{part['template']}' must be a valid content part."
            )
        return [source] if source else []
    elif part["type"] == "parts":
        sources = attrs[part["template"]]
        if not isinstance(sources, list):
            raise ValueError(
                f"When using 'parts' template, '{part['template']}' must be a list."
            )

        # validate each part is a valid content part
        for source in sources:
            if not isinstance(
                source,
                TextPart
                | ImagePart
                | ImageURLPart
                | AudioPart
                | AudioURLPart
                | CacheControlPart
                | DocumentPart,
            ):
                raise ValueError(
                    f"When using 'parts' template, '{part['template']}' must be a list of valid content parts."
                )
        return sources if sources else []
    elif part["type"] == "texts":
        sources = attrs[part["template"]]
        if not isinstance(sources, list):
            raise ValueError(
                f"When using 'texts' template, '{part['template']}' must be a list."
            )
        return (
            [TextPart(type="text", text=source) for source in sources]
            if sources
            else []
        )
    else:  # text type
        text = part["template"]
        if text in attrs:
            source = attrs[text]
            return [TextPart(type="text", text=source)]
        formatted_template = format_template(part["template"], attrs, strip=False)
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
        for part in _parse_parts(template.strip())
        for item in _construct_parts(part, attrs)
    ]

    if not parts:
        return None

    if len(parts) == 1 and parts[0].type == "text":
        return BaseMessageParam(role=role, content=parts[0].text)
    return BaseMessageParam(role=role, content=parts)
