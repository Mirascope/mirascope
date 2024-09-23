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

    class System(BaseMessageParam):
        def __init__(
            self,
            content: str
            | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
        ) -> None:
            super().__init__(
                content=convert_message_content_to_message_param_content(content),
                role="system",
            )

    class User(BaseMessageParam):
        def __init__(
            self,
            content: str
            | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
        ) -> None:
            super().__init__(
                content=convert_message_content_to_message_param_content(content),
                role="user",
            )

    class Assistant(BaseMessageParam):
        def __init__(
            self,
            content: str
            | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
        ) -> None:
            super().__init__(
                content=convert_message_content_to_message_param_content(content),
                role="assistant",
            )
