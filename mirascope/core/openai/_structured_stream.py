"""This module contains the OpenAI `structured_stream_decorator` function."""

from collections.abc import Generator
from functools import wraps
from typing import Callable, Generic, Iterable, ParamSpec, TypeVar

from openai import OpenAI
from openai._base_client import BaseClient
from openai.types.chat import ChatCompletionChunk
from pydantic import BaseModel

from ..base import BaseStructuredStream, _utils

# from ._utils import setup_extract
from .call_params import OpenAICallParams
from .dyanmic_config import OpenAIDynamicConfig
from .tool import OpenAITool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


class OpenAIStructuredStream(
    Generic[_ResponseModelT],
    BaseStructuredStream[ChatCompletionChunk, _ResponseModelT],
):
    """A class for streaming structured outputs from OpenAI's API."""

    def __iter__(self) -> Generator[_ResponseModelT, None, None]:
        """Iterates over the stream and extracts structured outputs."""
        json_output = ""
        for chunk in self.stream:
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
                yield _utils.extract_tool_return(self.response_model, json_output, True)
        yield _utils.extract_tool_return(self.response_model, json_output, False)


def structured_stream_decorator(
    fn: Callable[_P, OpenAIDynamicConfig],
    model: str,
    response_model: type[_ResponseModelT],
    client: BaseClient | None,
    call_params: OpenAICallParams,
) -> Callable[_P, Iterable[_ResponseModelT]]:
    assert response_model is not None
    tool = _utils.setup_extract_tool(response_model, OpenAITool)

    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> Iterable[_ResponseModelT]:
        # assert response_model is not None
        # fn_args = _utils.get_fn_args(fn, args, kwargs)
        # fn_return = fn(*args, **kwargs)
        # json_mode, messages, call_kwargs = setup_extract(
        #     fn, fn_args, fn_return, tool, call_params
        # )
        # _client = client or OpenAI()
        # return OpenAIStructuredStream(
        #     stream=(
        #         chunk
        #         for chunk in _client.chat.completions.create(
        #             model=model, stream=True, messages=messages, **call_kwargs
        #         )
        #     ),
        #     response_model=response_model,
        #     json_mode=json_mode,
        # )
        ...

    return inner
