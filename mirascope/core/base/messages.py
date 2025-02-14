from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from wave import Wave_read

from ._utils._convert_messages_to_message_params import (
    Image,
    convert_message_content_to_message_param_content,
)
from .message_param import (
    AudioPart,
    AudioURLPart,
    BaseMessageParam,
    CacheControlPart,
    DocumentPart,
    ImagePart,
    ImageURLPart,
    TextPart,
)
from .types import AudioSegment


class Messages:
    Type = (
        str
        | Sequence[
            str
            | TextPart
            | CacheControlPart
            | ImagePart
            | ImageURLPart
            | Image.Image
            | AudioPart
            | AudioURLPart
            | AudioSegment
            | Wave_read
            | DocumentPart
        ]
        | list[BaseMessageParam | Any]
        | BaseMessageParam
    )

    @classmethod
    def System(
        cls,
        content: str
        | Sequence[
            str
            | TextPart
            | CacheControlPart
            | ImagePart
            | ImageURLPart
            | Image.Image
            | AudioPart
            | AudioURLPart
            | AudioSegment
            | Wave_read
            | DocumentPart
        ],
    ) -> BaseMessageParam:
        return BaseMessageParam(
            role="system",
            content=convert_message_content_to_message_param_content(content),
        )

    @classmethod
    def User(
        cls,
        content: str
        | Sequence[
            str
            | TextPart
            | CacheControlPart
            | ImagePart
            | ImageURLPart
            | Image.Image
            | AudioPart
            | AudioURLPart
            | AudioSegment
            | Wave_read
            | DocumentPart
        ],
    ) -> BaseMessageParam:
        return BaseMessageParam(
            role="user",
            content=convert_message_content_to_message_param_content(content),
        )

    @classmethod
    def Assistant(
        cls,
        content: str
        | Sequence[
            str
            | TextPart
            | CacheControlPart
            | ImagePart
            | ImageURLPart
            | Image.Image
            | AudioPart
            | AudioURLPart
            | AudioSegment
            | Wave_read
            | DocumentPart
        ],
    ) -> BaseMessageParam:
        return BaseMessageParam(
            role="assistant",
            content=convert_message_content_to_message_param_content(content),
        )
