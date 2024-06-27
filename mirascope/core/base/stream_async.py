"""This module contains the base classes for async streaming responses from LLMs."""

from abc import ABC
from collections.abc import AsyncGenerator
from typing import Generic, TypeVar

from .call_response_chunk import BaseCallResponseChunk
from .tool import BaseTool

_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_UserMessageParamT = TypeVar("_UserMessageParamT")
_AssistantMessageParamT = TypeVar("_AssistantMessageParamT")
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)


class BaseAsyncStream(
    Generic[
        _BaseCallResponseChunkT,
        _UserMessageParamT,
        _AssistantMessageParamT,
        _BaseToolT,
    ],
    ABC,
):
    """A base class for async streaming responses from LLMs."""

    stream: AsyncGenerator[_BaseCallResponseChunkT, None]
    message_param_type: type[_AssistantMessageParamT]

    cost: float | None = None
    user_message_param: _UserMessageParamT | None = None
    message_param: _AssistantMessageParamT

    def __init__(
        self,
        stream: AsyncGenerator[_BaseCallResponseChunkT, None],
        message_param_type: type[_AssistantMessageParamT],
    ):
        """Initializes an instance of `BaseAsyncStream`."""
        self.stream = stream
        self.message_param_type = message_param_type

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[_BaseCallResponseChunkT, _BaseToolT | None], None]:
        """Iterates over the stream and stores useful information."""

        async def generator():
            content = ""
            async for chunk in self.stream:
                self.user_message_param = chunk.user_message_param
                content += chunk.content
                if chunk.cost is not None:
                    self.cost = chunk.cost
                yield chunk, None
            kwargs = {"role": "assistant"}
            if "message" in self.message_param_type.__annotations__:
                kwargs["message"] = content
            else:
                kwargs["content"] = content
            self.message_param = self.message_param_type(**kwargs)

        return generator()
