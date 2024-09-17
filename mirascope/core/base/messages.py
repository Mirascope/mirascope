"""This module contains the base class for message parameters."""

from __future__ import annotations

from collections.abc import Sequence

from . import AudioPart, BaseMessageParam, CacheControlPart, ImagePart, TextPart
from ._utils._get_message_params import (
    Image,
    get_content_from_message_sequence,
)


def _get_content_from_message(
    content: str | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
) -> str | list[TextPart | ImagePart | AudioPart | CacheControlPart]:
    if isinstance(content, str):
        return content
    return get_content_from_message_sequence(content)


class Messages:
    Type = (
        str
        | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart]
        | list[BaseMessageParam]
        | BaseMessageParam
    )

    class System(BaseMessageParam):
        def __init__(
            self,
            content: str
            | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
        ) -> None:
            super().__init__(content=_get_content_from_message(content), role="system")

    class User(BaseMessageParam):
        def __init__(
            self,
            content: str
            | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
        ) -> None:
            super().__init__(content=_get_content_from_message(content), role="user")

    class Assistant(BaseMessageParam):
        def __init__(
            self,
            content: str
            | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
        ) -> None:
            super().__init__(
                content=_get_content_from_message(content),
                role="assistant",
            )
