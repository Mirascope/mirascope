"""This module contains the Anthropic `structured_stream_async_decorator` function."""

from collections.abc import AsyncGenerator
from functools import wraps
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Generic,
    ParamSpec,
    TypeVar,
)

from anthropic import AsyncAnthropic
from anthropic.lib.streaming import MessageStreamEvent
from pydantic import BaseModel

from ..base import BaseAsyncStructuredStream, _utils

# from ._utils import setup_extract
from .call_params import AnthropicCallParams
from .dynamic_config import AnthropicDynamicConfig
from .tool import AnthropicTool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


class AnthropicAsyncStructuredStream(
    Generic[_ResponseModelT],
    BaseAsyncStructuredStream[MessageStreamEvent, _ResponseModelT],
):
    """A class for async streaming structured outputs from Anthropic's API."""

    def __aiter__(self) -> AsyncGenerator[_ResponseModelT, None]:
        """Iterates over the stream and extracts structured outputs."""

        async def generator():
            nonlocal self
            json_output = ""
            async for chunk in self.stream:
                if chunk.type == "content_block_delta":
                    if chunk.delta.type in ["text", "text_delta"]:
                        json_output += chunk.delta.text
                    elif chunk.delta.type == "input_json_delta":
                        json_output += chunk.delta.partial_json
                if json_output:
                    yield _utils.extract_tool_return(
                        self.response_model, json_output, True
                    )
            yield _utils.extract_tool_return(self.response_model, json_output, False)

        return generator()


def structured_stream_async_decorator(
    fn: Callable[_P, Awaitable[AnthropicDynamicConfig]],
    model: str,
    response_model: type[_ResponseModelT],
    call_params: AnthropicCallParams,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]:
    assert response_model is not None
    tool = _utils.setup_extract_tool(response_model, AnthropicTool)

    @wraps(fn)
    async def inner(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> AsyncIterable[_ResponseModelT]:
        # assert response_model is not None
        # fn_args = _utils.get_fn_args(fn, args, kwargs)
        # fn_return = await fn(*args, **kwargs)
        # json_mode, messages, call_kwargs = setup_extract(
        #     fn, fn_args, fn_return, tool, call_params
        # )
        # client = AsyncAnthropic()
        # return AnthropicAsyncStructuredStream(
        #     stream=(
        #         chunk
        #         async for chunk in await client.messages.create(
        #             model=model, stream=True, messages=messages, **call_kwargs
        #         )
        #     ),
        #     response_model=response_model,
        #     json_mode=json_mode,
        # )
        ...

    return inner
