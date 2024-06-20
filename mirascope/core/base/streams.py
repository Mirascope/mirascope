"""This module contains the base classes for streaming responses from LLMs."""

from abc import ABC
from collections.abc import AsyncGenerator, Generator
from typing import Any, Generic, TypeVar

from .call_response_chunk import BaseCallResponseChunk
from .tools import BaseTool

BaseCallResponseChunkT = TypeVar("BaseCallResponseChunkT", bound=BaseCallResponseChunk)
UserMessageParamT = TypeVar("UserMessageParamT", bound=Any)
AssistantMessageParamT = TypeVar("AssistantMessageParamT", bound=Any)
BaseToolT = TypeVar("BaseToolT", bound=BaseTool)


class BaseStream(
    Generic[
        BaseCallResponseChunkT,
        UserMessageParamT,
        AssistantMessageParamT,
        BaseToolT,
    ],
    ABC,
):
    """A base class for streaming responses from LLMs."""

    stream: Generator[BaseCallResponseChunkT, None, None]
    message_param_type: type[AssistantMessageParamT]

    cost: float | None = None
    user_message_param: UserMessageParamT | None = None
    message_param: AssistantMessageParamT

    def __init__(
        self,
        stream: Generator[BaseCallResponseChunkT, None, None],
        message_param_type: type[AssistantMessageParamT],
    ):
        """Initializes an instance of `BaseStream`."""
        self.stream = stream
        self.message_param_type = message_param_type

    def __iter__(
        self,
    ) -> Generator[tuple[BaseCallResponseChunkT, BaseToolT | None], None, None]:
        """Iterator over the stream and stores useful information."""
        content = ""
        for chunk in self.stream:
            content += chunk.content
            if chunk.cost is not None:
                self.cost = chunk.cost
            yield chunk, None
            self.user_message_param = chunk.user_message_param
        kwargs = {"role": "assistant"}
        if "message" in self.message_param_type.__annotations__:
            kwargs["message"] = content
        else:
            kwargs["content"] = content
        self.message_param = self.message_param_type(**kwargs)


class BaseAsyncStream(
    Generic[
        BaseCallResponseChunkT,
        UserMessageParamT,
        AssistantMessageParamT,
        BaseToolT,
    ],
    ABC,
):
    """A base class for async streaming responses from LLMs."""

    stream: AsyncGenerator[BaseCallResponseChunkT, None]
    message_param_type: type[AssistantMessageParamT]

    cost: float | None = None
    user_message_param: UserMessageParamT | None = None
    message_param: AssistantMessageParamT

    def __init__(
        self,
        stream: AsyncGenerator[BaseCallResponseChunkT, None],
        message_param_type: type[AssistantMessageParamT],
    ):
        """Initializes an instance of `BaseAsyncStream`."""
        self.stream = stream
        self.message_param_type = message_param_type

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[BaseCallResponseChunkT, BaseToolT | None], None]:
        """Iterates over the stream and stores useful information."""

        async def generator():
            content = ""
            async for chunk in self.stream:
                content += chunk.content
                if chunk.cost is not None:
                    self.cost = chunk.cost
                yield chunk, None
                self.user_message_param = chunk.user_message_param
            kwargs = {"role": "assistant"}
            if "message" in self.message_param_type.__annotations__:
                kwargs["message"] = content
            else:
                kwargs["content"] = content
            self.message_param = self.message_param_type(**kwargs)

        return generator()
