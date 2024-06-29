"""This module contains the OpenAI `stream_async_decorator` function."""

from collections.abc import AsyncGenerator
from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    ParamSpec,
)

from openai import AsyncAzureOpenAI, AsyncOpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_tool_call import Function

from ..base import BaseAsyncStream, BaseTool, _utils
from ._utils import (
    handle_chunk,
    openai_api_calculate_cost,
    setup_call,
)
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .dyanmic_config import OpenAIDynamicConfig
from .tool import OpenAITool

_P = ParamSpec("_P")


class OpenAIAsyncStream(
    BaseAsyncStream[
        OpenAICallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        OpenAITool,
    ],
):
    """A class for streaming responses from OpenAI's API."""

    provider: str = "openai"

    def __init__(
        self,
        stream: AsyncGenerator[OpenAICallResponseChunk, None],
        prompt_template: str,
        fn_args: dict[str, Any],
        call_params: OpenAICallParams,
    ):
        """Initializes an instance of `OpenAIAsyncStream`."""
        super().__init__(
            stream,
            ChatCompletionAssistantMessageParam,
            prompt_template,
            fn_args,
            call_params,
        )

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[OpenAICallResponseChunk, OpenAITool | None], None]:
        """Iterator over the stream and constructs tools as they are streamed."""
        stream = super().__aiter__()

        async def generator():
            current_tool_call = ChatCompletionMessageToolCall(
                id="", function=Function(arguments="", name=""), type="function"
            )
            current_tool_type, tool_calls = None, []
            async for chunk, _ in stream:
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

        return generator()

    @classmethod
    def tool_message_params(cls, tools_and_outputs):
        """Returns the tool message parameters for tool call results."""
        return OpenAICallResponse.tool_message_params(tools_and_outputs)


def stream_async_decorator(
    fn: Callable[_P, Awaitable[OpenAIDynamicConfig]],
    model: str,
    tools: list[type[BaseTool] | Callable] | None,
    call_params: OpenAICallParams,
) -> Callable[_P, Awaitable[OpenAIAsyncStream]]:
    @wraps(fn)
    async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> OpenAIAsyncStream:
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = await fn(*args, **kwargs)
        prompt_template, messages, tool_types, call_kwargs = setup_call(
            fn, fn_args, fn_return, tools, call_params
        )
        client = AsyncOpenAI()

        if not isinstance(client, AsyncAzureOpenAI):
            call_kwargs["stream_options"] = {"include_usage": True}

        stream = await client.chat.completions.create(
            model=model, stream=True, messages=messages, **call_kwargs
        )

        async def generator():
            async for chunk in stream:
                yield OpenAICallResponseChunk(
                    tags=fn.__annotations__.get("tags", []),
                    chunk=chunk,
                    user_message_param=messages[-1]
                    if messages[-1]["role"] == "user"
                    else None,
                    tool_types=tool_types,
                    cost=openai_api_calculate_cost(chunk.usage, chunk.model),
                )

        return OpenAIAsyncStream(generator(), prompt_template, fn_args, call_params)

    return inner_async
