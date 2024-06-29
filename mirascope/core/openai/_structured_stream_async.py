"""This module contains the OpenAI `structured_stream_async_decorator` function."""

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

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionChunk
from pydantic import BaseModel

from ..base import BaseAsyncStructuredStream, _utils

# from ._utils import setup_extract
from .call_params import OpenAICallParams
from .dyanmic_config import OpenAIDynamicConfig
from .tool import OpenAITool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


class OpenAIAsyncStructuredStream(
    Generic[_ResponseModelT],
    BaseAsyncStructuredStream[ChatCompletionChunk, _ResponseModelT],
):
    """A class for async streaming structured outputs from OpenAI's API."""

    def __aiter__(self) -> AsyncGenerator[_ResponseModelT, None]:
        """Iterates over the stream and extracts structured outputs."""

        async def generator():
            nonlocal self
            json_output = ""
            async for chunk in self.stream:
                if (
                    self.json_mode
                    and (content := chunk.choices[0].delta.content) is not None
                ):
                    json_output += content
                elif (
                    (tool_calls := chunk.choices[0].delta.tool_calls)
                    and (function := tool_calls[0].function)
                    and (arguments := function.arguments)
                ):
                    json_output += arguments
                else:
                    ValueError("No tool call or JSON object found in response.")
                if json_output:
                    yield _utils.extract_tool_return(
                        self.response_model, json_output, True
                    )
            yield _utils.extract_tool_return(self.response_model, json_output, False)

        return generator()


def structured_stream_async_decorator(
    fn: Callable[_P, Awaitable[OpenAIDynamicConfig]],
    model: str,
    response_model: type[_ResponseModelT],
    call_params: OpenAICallParams,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]:
    assert response_model is not None
    tool = _utils.setup_extract_tool(response_model, OpenAITool)

    @wraps(fn)
    async def inner_async(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> AsyncIterable[_ResponseModelT]:
        # assert response_model is not None
        # fn_args = _utils.get_fn_args(fn, args, kwargs)
        # fn_return = await fn(*args, **kwargs)
        # json_mode, messages, call_kwargs = setup_extract(
        #     fn, fn_args, fn_return, tool, call_params
        # )
        # client = AsyncOpenAI()
        # return OpenAIAsyncStructuredStream(
        #     stream=(
        #         chunk
        #         async for chunk in await client.chat.completions.create(
        #             model=model, stream=True, messages=messages, **call_kwargs
        #         )
        #     ),
        #     response_model=response_model,
        #     json_mode=json_mode,
        # )
        ...

    return inner_async
