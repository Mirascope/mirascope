"""This module contains the Gemini `structured_stream_async_decorator` function."""

import json
from collections.abc import AsyncGenerator
from functools import wraps
from typing import AsyncIterable, Awaitable, Callable, Generic, ParamSpec, TypeVar

from google.generativeai import GenerativeModel  # type: ignore
from google.generativeai.types import GenerateContentResponse
from pydantic import BaseModel

from ..base import BaseAsyncStructuredStream, _utils

# from ._utils import setup_extract
from .call_params import GeminiCallParams
from .dynamic_config import GeminiDynamicConfig
from .tool import GeminiTool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


class GeminiAsyncStructuredStream(
    Generic[_ResponseModelT],
    BaseAsyncStructuredStream[GenerateContentResponse, _ResponseModelT],
):
    """A class for streaming structured outputs from Gemini's API."""

    def __aiter__(self) -> AsyncGenerator[_ResponseModelT, None]:
        """Iterates over the stream and extracts structured outputs."""

        async def generator():
            nonlocal self
            json_output = ""
            async for chunk in self.stream:
                if (
                    self.json_mode
                    and (content := chunk.candidates[0].content.parts[0].text)
                    is not None
                ):
                    print(content)
                    json_output += content
                elif (
                    tool_calls := chunk.candidates[0].content.parts[0].function_call
                ) and (arguments := tool_calls.args):
                    json_output += json.dumps(dict(arguments))
                else:
                    ValueError("No tool call or JSON object found in response.")
                if json_output:
                    yield _utils.extract_tool_return(
                        self.response_model, json_output, True
                    )
            yield _utils.extract_tool_return(self.response_model, json_output, False)

        return generator()


def structured_stream_async_decorator(
    fn: Callable[_P, Awaitable[GeminiDynamicConfig]],
    model: str,
    response_model: type[_ResponseModelT],
    call_params: GeminiCallParams,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]:
    assert response_model is not None
    tool = _utils.setup_extract_tool(response_model, GeminiTool)

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
        # client = GenerativeModel(model_name=model)
        # stream = client.generate_content_async(
        #     messages,
        #     stream=True,
        #     **call_kwargs,
        # )
        # return GeminiAsyncStructuredStream(
        #     stream=stream,
        #     response_model=response_model,
        #     json_mode=json_mode,
        # )
        ...

    return inner_async
