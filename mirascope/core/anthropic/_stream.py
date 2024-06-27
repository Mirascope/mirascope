"""This module contains the Anthropic `stream_decorator` function."""

from collections.abc import Generator
from functools import wraps
from typing import Callable, ParamSpec

from anthropic import Anthropic
from anthropic.types import (
    MessageParam,
    MessageStartEvent,
    RawMessageDeltaEvent,
    TextBlock,
    ToolUseBlock,
)

from ..base import BaseStream, BaseTool, _utils
from ._utils import anthropic_api_calculate_cost, handle_chunk, setup_call
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .call_response_chunk import AnthropicCallResponseChunk
from .function_return import AnthropicDynamicConfig
from .tool import AnthropicTool

_P = ParamSpec("_P")


class AnthropicStream(
    BaseStream[AnthropicCallResponseChunk, MessageParam, MessageParam, AnthropicTool]
):
    """A class for streaming responses from Anthropic's API."""

    def __init__(
        self,
        stream: Generator[AnthropicCallResponseChunk, None, None],
    ):
        """Initializes an instance of `AnthropicStream`."""
        super().__init__(stream, MessageParam)

    def __iter__(
        self,
    ) -> Generator[tuple[AnthropicCallResponseChunk, AnthropicTool | None], None, None]:
        """Iterator over the stream and constructs tools as they are streamed."""
        current_text_block = TextBlock(id="", text="", type="text")
        current_tool_call = ToolUseBlock(id="", input={}, name="", type="tool_use")
        current_tool_type, content, buffer = None, [], ""
        for chunk, _ in super().__iter__():
            buffer, tool, current_tool_call, current_tool_type = handle_chunk(
                buffer, chunk, current_tool_call, current_tool_type
            )
            if tool is not None:
                yield chunk, tool
                if current_text_block.text:
                    content.append(current_text_block)
                    current_text_block = TextBlock(id="", text="", type="text")
                content.append(tool.tool_call)
            else:
                yield chunk, None
                current_text_block.text += chunk.content
        self.message_param["content"] = content

    @classmethod
    def tool_message_params(cls, tools_and_outputs):
        """Returns the tool message parameters for tool call results."""
        return AnthropicCallResponse.tool_message_params(tools_and_outputs)


def stream_decorator(
    fn: Callable[_P, AnthropicDynamicConfig],
    model: str,
    tools: list[type[BaseTool] | Callable] | None,
    call_params: AnthropicCallParams,
) -> Callable[_P, AnthropicStream]:
    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> AnthropicStream:
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = fn(*args, **kwargs)
        _, messages, tool_types, call_kwargs = setup_call(
            fn, fn_args, fn_return, tools, call_params
        )
        client = Anthropic()

        stream = client.messages.create(
            model=model, stream=True, messages=messages, **call_kwargs
        )

        def generator():
            usage, model = None, ""
            for chunk in stream:
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

        return AnthropicStream(generator())

    return inner
