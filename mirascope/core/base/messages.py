from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ._utils._convert_messages_to_message_params import (
    Image,
    convert_message_content_to_message_param_content,
)
from .message_param import AudioPart, BaseMessageParam, ImagePart, TextPart


class Messages:
    Type = (
        str
        | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart]
        | list[BaseMessageParam | Any]
        | BaseMessageParam
    )

    @classmethod
    def System(
        cls,
        content: str | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
    ) -> BaseMessageParam:
        return BaseMessageParam(
            role="system",
            content=convert_message_content_to_message_param_content(content),
        )

    @classmethod
    def User(
        cls,
        content: str | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
    ) -> BaseMessageParam:
        return BaseMessageParam(
            role="user",
            content=convert_message_content_to_message_param_content(content),
        )

    @classmethod
    def Assistant(
        cls,
        content: str | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
    ) -> BaseMessageParam:
        return BaseMessageParam(
            role="assistant",
            content=convert_message_content_to_message_param_content(content),
        )
