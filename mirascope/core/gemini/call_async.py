"""The `gemini_call_async` decorator for easy Gemini API typed functions."""

from functools import partial
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Literal,
    ParamSpec,
    TypeVar,
    Unpack,
    overload,
)

from google.generativeai.types import GenerateContentResponse
from pydantic import BaseModel

from ..base import BaseTool, _utils
from ._create_async import create_async_decorator
from ._extract_async import extract_async_decorator
from ._stream_async import GeminiAsyncStream, stream_async_decorator
from ._structured_stream_async import structured_stream_async_decorator
from .call_params import GeminiCallParams
from .call_response import GeminiCallResponse
from .call_response_chunk import GeminiCallResponseChunk
from .function_return import GeminiCallFunctionReturn

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)
_ParsedOutputT = TypeVar("_ParsedOutputT")


@overload
def gemini_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    **call_params: Unpack[GeminiCallParams],
) -> Callable[
    [Callable[_P, Awaitable[GeminiCallFunctionReturn]]],
    Callable[_P, Awaitable[GeminiCallResponse]],
]: ...  # pragma: no cover


@overload
def gemini_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    **call_params: Unpack[GeminiCallParams],
) -> Callable[
    [Callable[_P, Awaitable[GeminiCallFunctionReturn]]],
    Callable[_P, Awaitable[_ResponseModelT]],
]: ...  # pragma: no cover


@overload
def gemini_call_async(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    **call_params: Unpack[GeminiCallParams],
) -> Callable[
    [Callable[_P, Awaitable[GeminiCallFunctionReturn]]],
    Callable[_P, Awaitable[GeminiAsyncStream[GenerateContentResponse]]],
]: ...  # pragma: no cover


@overload
def gemini_call_async(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    **call_params: Unpack[GeminiCallParams],
) -> Callable[
    [Callable[_P, Awaitable[GeminiCallFunctionReturn]]],
    Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]],
]: ...  # pragma: no cover


def gemini_call_async(
    model: str,
    *,
    stream: bool = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[GeminiCallResponse], _ParsedOutputT]
    | Callable[[GeminiCallResponseChunk], _ParsedOutputT]
    | None = None,
    **call_params: Unpack[GeminiCallParams],
) -> Callable[
    [Callable[_P, GeminiCallFunctionReturn]],
    Callable[
        _P,
        Awaitable[GeminiCallResponse | _ParsedOutputT]
        | Awaitable[GeminiAsyncStream[GenerateContentResponse | _ParsedOutputT]]
        | Awaitable[_ResponseModelT]
        | Awaitable[AsyncIterable[_ResponseModelT]],
    ],
]:
    '''A decorator for calling the Gemini API with a typed function.

    This decorator is used to wrap a typed function that calls the Gemini API. It parses
    the docstring of the wrapped function as the messages array and templates the input
    arguments for the function into each message's template.

    Example:

    ```python
    @gemini_call(model="gemini-1.5-pro")
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    response = recommend_book("fantasy")
    ```

    Args:
        model: The Gemini model to use in the API call.
        stream: Whether to stream the response from the API call.
        tools: The tools to use in the Gemini API call.
        **call_params: The `GeminiCallParams` call parameters to use in the API call.

    Returns:
        The decorator for turning a typed function into an Gemini API call.
    '''

    if response_model and output_parser:
        raise ValueError("Cannot use both `response_model` and `output_parser`.")

    if response_model:
        if stream:
            return partial(
                structured_stream_async_decorator,
                model=model,
                response_model=response_model,
                call_params=call_params,
            )
        else:
            return partial(
                extract_async_decorator,
                model=model,
                response_model=response_model,
                call_params=call_params,
            )
    if stream:
        return partial(
            stream_async_decorator,
            model=model,
            tools=tools,
            output_parser=output_parser,
            call_params=call_params,
        )
    return partial(
        create_async_decorator,
        model=model,
        tools=tools,
        output_parser=output_parser,
        call_params=call_params,
    )
