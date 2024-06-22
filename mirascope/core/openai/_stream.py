"""This module contains the OpenAI `stream_decorator` function."""

import inspect
from collections.abc import Generator
from functools import wraps
from typing import Callable, Generic, ParamSpec, TypeVar

from openai import AzureOpenAI, OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_tool_call import Function

from ..base import BaseStream, BaseTool
from ._utils import handle_chunk, openai_api_calculate_cost, setup_call
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .function_return import OpenAICallFunctionReturn
from .tool import OpenAITool

_P = ParamSpec("_P")
_OutputT = TypeVar("_OutputT")


class OpenAIStream(
    BaseStream[
        OpenAICallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        OpenAITool,
        _OutputT,
    ],
    Generic[_OutputT],
):
    """A class for streaming responses from OpenAI's API."""

    def __init__(
        self,
        stream: Generator[OpenAICallResponseChunk, None, None],
        output_parser: Callable[[OpenAICallResponseChunk], _OutputT] | None,
    ):
        """Initializes an instance of `OpenAIStream`."""
        super().__init__(stream, ChatCompletionAssistantMessageParam, output_parser)

    def __iter__(
        self,
    ) -> Generator[tuple[_OutputT, OpenAITool | None], None, None]:
        """Iterator over the stream and constructs tools as they are streamed."""
        output_parser = self.output_parser if self.output_parser else lambda x: x
        self.output_parser = None
        current_tool_call = ChatCompletionMessageToolCall(
            id="", function=Function(arguments="", name=""), type="function"
        )
        current_tool_type, tool_calls = None, []
        for chunk, _ in super().__iter__():
            if not chunk.tool_types or not chunk.tool_calls:  # type: ignore
                if current_tool_type:
                    yield (
                        output_parser(chunk),  # type: ignore
                        current_tool_type.from_tool_call(current_tool_call),
                    )
                    tool_calls.append(current_tool_call)
                    current_tool_type = None
                else:
                    yield output_parser(chunk), None  # type: ignore
            tool, current_tool_call, current_tool_type = handle_chunk(
                chunk,  # type: ignore
                current_tool_call,
                current_tool_type,
            )
            if tool is not None:
                yield output_parser(chunk), tool  # type: ignore
                tool_calls.append(tool.tool_call)
        if tool_calls:
            self.message_param["tool_calls"] = tool_calls  # type: ignore

    @classmethod
    def tool_message_params(cls, tools_and_outputs):
        """Returns the tool message parameters for tool call results."""
        return OpenAICallResponse.tool_message_params(tools_and_outputs)


def stream_decorator(
    fn: Callable[_P, OpenAICallFunctionReturn],
    model: str,
    tools: list[type[BaseTool] | Callable] | None,
    output_parser: Callable[[OpenAICallResponseChunk], _OutputT] | None,
    call_params: OpenAICallParams,
) -> Callable[_P, OpenAIStream[OpenAICallResponseChunk | _OutputT]]:
    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> OpenAIStream:
        fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
        fn_return = fn(*args, **kwargs)
        _, messages, tool_types, call_kwargs = setup_call(
            fn, fn_args, fn_return, tools, call_params
        )
        client = OpenAI()

        if not isinstance(client, AzureOpenAI):
            call_kwargs["stream_options"] = {"include_usage": True}

        stream = client.chat.completions.create(
            model=model, stream=True, messages=messages, **call_kwargs
        )

        def generator():
            for chunk in stream:
                yield OpenAICallResponseChunk(
                    chunk=chunk,
                    user_message_param=messages[-1]
                    if messages[-1]["role"] == "user"
                    else None,
                    tool_types=tool_types,
                    cost=openai_api_calculate_cost(chunk.usage, chunk.model),
                )

        return OpenAIStream(generator(), output_parser)

    return inner
