"""This module contains the Anthropic `stream_async_decorator` function."""

from collections.abc import AsyncGenerator
from functools import wraps
from typing import (
    Awaitable,
    Callable,
    Generic,
    ParamSpec,
    TypeVar,
)

from anthropic import AsyncAnthropic
from anthropic.types import (
    MessageParam,
    MessageStartEvent,
    RawMessageDeltaEvent,
    TextBlock,
    ToolUseBlock,
)

from ..base import BaseAsyncStream, BaseTool, _utils
from ._utils import (
    anthropic_api_calculate_cost,
    handle_chunk,
    setup_call,
)
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .call_response_chunk import AnthropicCallResponseChunk
from .function_return import AnthropicCallFunctionReturn
from .tool import AnthropicTool

_P = ParamSpec("_P")
_OutputT = TypeVar("_OutputT")


class AnthropicAsyncStream(
    BaseAsyncStream[
        AnthropicCallResponseChunk,
        MessageParam,
        MessageParam,
        AnthropicTool,
        _OutputT,
    ],
    Generic[_OutputT],
):
    """A class for streaming responses from Anthropic's API."""

    def __init__(
        self,
        stream: AsyncGenerator[AnthropicCallResponseChunk, None],
        output_parser: Callable[[AnthropicCallResponseChunk], _OutputT] | None,
    ):
        """Initializes an instance of `AnthropicAsyncStream`."""
        super().__init__(stream, MessageParam, output_parser)

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[_OutputT, AnthropicTool | None], None]:
        """Iterator over the stream and constructs tools as they are streamed."""
        output_parser = self.output_parser if self.output_parser else lambda x: x
        self.output_parser = None
        stream = super().__aiter__()

        async def generator():
            current_tool_call = ToolUseBlock(id="", input={}, name="", type="tool_use")
            current_text_block = TextBlock(id="", text="", type="text")
            current_tool_type, content, buffer = None, [], ""
            async for chunk, _ in stream:
                async for chunk, _ in stream:
                    buffer, tool, current_tool_call, current_tool_type = handle_chunk(
                        buffer, chunk, current_tool_call, current_tool_type
                    )
                    if tool is not None:
                        yield output_parser(chunk), tool
                        if current_text_block.text:
                            content.append(current_text_block)
                            current_text_block = TextBlock(id="", text="", type="text")
                        content.append(tool.tool_call)
                    else:
                        yield output_parser(chunk), None
                        current_text_block.text += chunk.content
                self.message_param["content"] = content

        return generator()

    @classmethod
    def tool_message_params(cls, tools_and_outputs):
        """Returns the tool message parameters for tool call results."""
        return AnthropicCallResponse.tool_message_params(tools_and_outputs)


def stream_async_decorator(
    fn: Callable[_P, Awaitable[AnthropicCallFunctionReturn]],
    model: str,
    tools: list[type[BaseTool] | Callable] | None,
    output_parser: Callable[[AnthropicCallResponseChunk], _OutputT] | None,
    call_params: AnthropicCallParams,
) -> Callable[
    _P, Awaitable[AnthropicAsyncStream[AnthropicCallResponseChunk | _OutputT]]
]:
    @wraps(fn)
    async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> AnthropicAsyncStream:
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = await fn(*args, **kwargs)
        _, messages, tool_types, call_kwargs = setup_call(
            fn, fn_args, fn_return, tools, call_params
        )
        client = AsyncAnthropic()

        stream = await client.messages.create(
            model=model, stream=True, messages=messages, **call_kwargs
        )

        async def generator():
            usage, model = None, ""
            async for chunk in stream:
                if isinstance(chunk, MessageStartEvent):
                    usage = chunk.message.usage
                    model = chunk.message.model
                if isinstance(chunk, RawMessageDeltaEvent):
                    usage.output_tokens += chunk.usage.output_tokens
                yield AnthropicCallResponseChunk(
                    tags=fn.__annotations__.get("tags", []),
                    chunk=chunk,
                    user_message_param=messages[-1]
                    if messages[-1]["role"] == "user"
                    else None,
                    tool_types=tool_types,
                    cost=anthropic_api_calculate_cost(usage, model),
                )

        return AnthropicAsyncStream(generator(), output_parser)

    return inner_async
