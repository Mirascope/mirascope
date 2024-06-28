"""This module contains the OpenAI `stream_decorator` function."""

from collections.abc import Generator
from functools import wraps
from typing import Any, Callable, ParamSpec

from openai import AzureOpenAI, OpenAI
from openai._base_client import BaseClient
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_tool_call import Function

from ..base import BaseStream, BaseTool, _utils
from ._utils import handle_chunk, openai_api_calculate_cost, setup_call
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .function_return import OpenAIDynamicConfig
from .tool import OpenAITool

_P = ParamSpec("_P")


class OpenAIStream(
    BaseStream[
        OpenAICallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        OpenAITool,
    ]
):
    """A class for streaming responses from OpenAI's API."""

    provider: str = "openai"

    def __init__(
        self,
        stream: Generator[OpenAICallResponseChunk, None, None],
        prompt_template: str,
        fn_args: dict[str, Any],
        call_params: OpenAICallParams,
    ):
        """Initializes an instance of `OpenAIStream`."""
        super().__init__(
            stream,
            ChatCompletionAssistantMessageParam,
            prompt_template,
            fn_args,
            call_params,
        )

    def __iter__(
        self,
    ) -> Generator[tuple[OpenAICallResponseChunk, OpenAITool | None], None, None]:
        """Iterator over the stream and constructs tools as they are streamed."""
        current_tool_call = ChatCompletionMessageToolCall(
            id="", function=Function(arguments="", name=""), type="function"
        )
        current_tool_type, tool_calls = None, []
        for chunk, _ in super().__iter__():
            if not chunk.tool_types or not chunk.tool_calls:
                if current_tool_type:
                    yield (
                        chunk,
                        current_tool_type.from_tool_call(current_tool_call),
                    )
                    tool_calls.append(current_tool_call)
                    current_tool_type = None
                else:
                    yield chunk, None
            tool, current_tool_call, current_tool_type = handle_chunk(
                chunk,
                current_tool_call,
                current_tool_type,
            )
            if tool is not None:
                yield chunk, tool
                tool_calls.append(tool.tool_call)
        if tool_calls:
            self.message_param["tool_calls"] = tool_calls  # type: ignore

    @classmethod
    def tool_message_params(cls, tools_and_outputs):
        """Returns the tool message parameters for tool call results."""
        return OpenAICallResponse.tool_message_params(tools_and_outputs)


def stream_decorator(
    fn: Callable[_P, OpenAIDynamicConfig],
    model: str,
    tools: list[type[BaseTool] | Callable] | None,
    client: BaseClient | None,
    call_params: OpenAICallParams,
) -> Callable[_P, OpenAIStream]:
    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> OpenAIStream:
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = fn(*args, **kwargs)
        prompt_template, messages, tool_types, call_kwargs = setup_call(
            fn, fn_args, fn_return, tools, call_params
        )
        _client = client or OpenAI()

        if not isinstance(_client, AzureOpenAI):
            call_kwargs["stream_options"] = {"include_usage": True}

        stream = _client.chat.completions.create(
            model=model, stream=True, messages=messages, **call_kwargs
        )

        def generator():
            for chunk in stream:
                yield OpenAICallResponseChunk(
                    tags=fn.__annotations__.get("tags", []),
                    chunk=chunk,
                    user_message_param=messages[-1]
                    if messages[-1]["role"] == "user"
                    else None,
                    tool_types=tool_types,
                    cost=openai_api_calculate_cost(chunk.usage, chunk.model),
                )

        return OpenAIStream(generator(), prompt_template, fn_args, call_params)

    return inner
