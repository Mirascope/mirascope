"""The `openai_call` decorator for functions as LLM calls."""

from functools import partial
from typing import (
    Callable,
    Iterable,
    Literal,
    ParamSpec,
    TypeVar,
    Unpack,
    overload,
)

from pydantic import BaseModel

from ..base import BaseTool, _utils
from ._call import call_decorator
from ._extract import extract_decorator
from ._stream import OpenAIStream, stream_decorator
from ._structured_stream import structured_stream_decorator
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .function_return import OpenAICallFunctionReturn

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


@overload
def openai_call(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, OpenAICallFunctionReturn]],
    Callable[_P, OpenAICallResponse],
]: ...  # pragma: no cover


@overload
def openai_call(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, OpenAICallFunctionReturn]],
    Callable[_P, _ResponseModelT],
]: ...  # pragma: no cover


@overload
def openai_call(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, OpenAICallFunctionReturn]],
    Callable[_P, OpenAIStream],
]: ...  # pragma: no cover


@overload
def openai_call(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, OpenAICallFunctionReturn]],
    Callable[_P, Iterable[_ResponseModelT]],
]: ...  # pragma: no cover


def openai_call(
    model: str,
    *,
    stream: bool = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, OpenAICallFunctionReturn]],
    Callable[
        _P,
        OpenAICallResponse | OpenAIStream | _ResponseModelT | Iterable[_ResponseModelT],
    ],
]:
    '''A decorator for calling the OpenAI API with a typed function.

    This decorator is used to wrap a typed function that calls the OpenAI API. It parses
    the docstring of the wrapped function as the messages array and templates the input
    arguments for the function into each message's template.

    Example:

    ```python
    @openai_call(model="gpt-4o")
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    response = recommend_book("fantasy")
    ```

    Args:
        model: The OpenAI model to use in the API call.
        stream: Whether to stream the response from the API call.
        tools: The tools to use in the OpenAI API call.
        **call_params: The `OpenAICallParams` call parameters to use in the API call.

    Returns:
        The decorator for turning a typed function into an OpenAI API call.
    '''

    if response_model:
        if stream:
            return partial(
                structured_stream_decorator,
                model=model,
                response_model=response_model,
                call_params=call_params,
            )
        else:
            return partial(
                extract_decorator,
                model=model,
                response_model=response_model,
                call_params=call_params,
            )
    if stream:
        return partial(
            stream_decorator, model=model, tools=tools, call_params=call_params
        )
    return partial(call_decorator, model=model, tools=tools, call_params=call_params)
