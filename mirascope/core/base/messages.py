from __future__ import annotations

from collections.abc import Sequence

from . import AudioPart, BaseMessageParam, ImagePart, TextPart
from ._utils._convert_messages_to_message_params import (
    Image,
    convert_message_content_to_message_param_content,
)


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
