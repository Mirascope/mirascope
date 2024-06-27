"""This module contains the base classes for streaming responses from LLMs."""

from abc import ABC
from collections.abc import Generator
from typing import Generic, TypeVar

from .call_response_chunk import BaseCallResponseChunk
from .tool import BaseTool

_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_UserMessageParamT = TypeVar("_UserMessageParamT")
_AssistantMessageParamT = TypeVar("_AssistantMessageParamT")
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)


class BaseStream(
    Generic[
        _BaseCallResponseChunkT,
        _UserMessageParamT,
        _AssistantMessageParamT,
        _BaseToolT,
    ],
    ABC,
):
    """A base class for streaming responses from LLMs."""

    stream: Generator[_BaseCallResponseChunkT, None, None]
    message_param_type: type[_AssistantMessageParamT]
    model: str | None = None
    cost: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    user_message_param: _UserMessageParamT | None = None
    message_param: _AssistantMessageParamT

    def __init__(
        self,
        stream: Generator[_BaseCallResponseChunkT, None, None],
        message_param_type: type[_AssistantMessageParamT],
    ):
        """Initializes an instance of `BaseStream`."""
        self.stream = stream
        self.message_param_type = message_param_type

    def __iter__(
        self,
    ) -> Generator[tuple[_BaseCallResponseChunkT, _BaseToolT | None], None, None]:
        """Iterator over the stream and stores useful information."""
        content = ""
        try:
            while True:
                chunk = next(self.stream)
                self.user_message_param = chunk.user_message_param
                content += chunk.content
                if chunk.cost is not None:
                    self.cost = chunk.cost
                if chunk.input_tokens is not None:
                    self.input_tokens = chunk.input_tokens
                if chunk.output_tokens is not None:
                    self.output_tokens = chunk.output_tokens
                if chunk.model is not None:
                    self.model = chunk.model
                yield chunk, None
        except StopIteration as e:
            print(f"\nRETURN VALUE: {e.value}")
        kwargs = {"role": "assistant"}
        if "message" in self.message_param_type.__annotations__:
            kwargs["message"] = content
        else:
            kwargs["content"] = content
        self.message_param = self.message_param_type(**kwargs)
