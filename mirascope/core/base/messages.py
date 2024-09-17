from __future__ import annotations

from collections.abc import Sequence

from . import AudioPart, BaseMessageParam, ImagePart, TextPart
from ._utils._convert_messages_to_message_params import (
    Image,
    get_content_from_message,
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
            super().__init__(content=get_content_from_message(content), role="system")

    class User(BaseMessageParam):
        def __init__(
            self,
            content: str
            | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
        ) -> None:
            super().__init__(content=get_content_from_message(content), role="user")

    class Assistant(BaseMessageParam):
        def __init__(
            self,
            content: str
            | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
        ) -> None:
            super().__init__(
                content=get_content_from_message(content),
                role="assistant",
            )
