from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import (
    Any,
    Literal,
    TypeAlias,
    TypeVar,
)

from black.trans import defaultdict
from pydantic import BaseModel

from mirascope.beta.realtime.base._utils._protocols import (
    Context,
    ReceiverFunc,
    SenderFunc,
)

ResponseType: TypeAlias = Literal[
    "text",
    "audio",
    "text_chunk",
    "audio_chunk",
    "audio_transcript",
    "audio_transcript_chunk",
]


class BaseResponse(BaseModel):
    content: str


_ResponseT = TypeVar("_ResponseT", bound=BaseResponse)
_ConnectionT = TypeVar("_ConnectionT")
# TODO: Improve the type of response
Response: TypeAlias = Any


class BaseRealtime(ABC):
    def __init__(self, model: str, context: Context, **client_configs: dict[str, Any]) -> None:
        self.model = model
        self.context = context
        self.senders: list[SenderFunc] = []
        self.receivers: defaultdict[ResponseType, ReceiverFunc] = defaultdict(list)

    @abstractmethod
    async def run(self) -> None: ...

    @abstractmethod
    def is_running(self) -> bool: ...

    def sender(self) -> Callable[[SenderFunc[_ResponseT]], SenderFunc[_ResponseT]]:
        def inner(func: SenderFunc[_ResponseT]) -> SenderFunc[_ResponseT]:
            self.senders.append(func)
            return func

        return inner

    def receiver(
        self, response_type: ResponseType
    ) -> Callable[[ReceiverFunc[_ResponseT]], ReceiverFunc]:
        def inner(func: ReceiverFunc[_ResponseT]) -> ReceiverFunc[_ResponseT]:
            self.receivers[response_type].append(func)
            return func

        return inner


_RealtimeT = TypeVar("_RealtimeT", bound=BaseRealtime)
