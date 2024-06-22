"""The `openai_call_async` decorator for easy OpenAI API typed functions."""

from functools import partial
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Literal,
    NoReturn,
    ParamSpec,
    TypeVar,
    Unpack,
    overload,
)

from pydantic import BaseModel

from ..base import BaseTool, _utils
from ._create_async import create_async_decorator
from ._extract_async import extract_async_decorator
from ._stream_async import OpenAIAsyncStream, stream_async_decorator
from ._structured_stream_async import structured_stream_async_decorator
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .function_return import OpenAICallFunctionReturn

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)
_ParsedOutputT = TypeVar("_ParsedOutputT")


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[_P, Awaitable[OpenAICallResponse]],
]:
    ...  # pragma: no cover


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: Callable[[OpenAICallResponse], _ParsedOutputT],
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[_P, Awaitable[_ParsedOutputT]],
]:
    ...  # pragma: no cover


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[True] = True,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[_P, Awaitable[OpenAIAsyncStream]],
]:
    ...  # pragma: no cover


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[True] = True,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: Callable[[OpenAICallResponse], _ParsedOutputT],
    **call_params: Unpack[OpenAICallParams],
) -> NoReturn:
    ...  # pragma: no cover


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[_P, Awaitable[_ResponseModelT]],
]:
    ...  # pragma: no cover


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: Callable[[OpenAICallResponse], _ParsedOutputT],
    **call_params: Unpack[OpenAICallParams],
) -> NoReturn:
    ...  # pragma: no cover


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]],
]:
    ...  # pragma: no cover


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: Callable[[OpenAICallResponse], _ParsedOutputT],
    **call_params: Unpack[OpenAICallParams],
) -> NoReturn:
    ...  # pragma: no cover


def openai_call_async(
    model: str,
    *,
    stream: bool = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[OpenAICallResponse], _ParsedOutputT] | None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[
        _P,
        Awaitable[OpenAICallResponse | _ParsedOutputT]
        | Awaitable[OpenAIAsyncStream]
        | Awaitable[_ResponseModelT]
        | Awaitable[AsyncIterable[_ResponseModelT]],
    ],
]:
    '''A decorator for calling the AsyncOpenAI API with a typed function.

    This decorator is used to wrap a typed function that calls the OpenAI API. It parses
    the docstring of the wrapped function as the messages array and templates the input
    arguments for the function into each message's template.

    Example:

    ```python
    @openai_call_async(model="gpt-4o")
    async def recommend_book(genre: str):
        """Recommend a {genre} book."""

    async def run():
        response = await recommend_book("fantasy")

    asyncio.run(run())
    ```

    Args:
        model: The OpenAI model to use in the API call.
        stream: Whether to stream the response from the API call.
        tools: The tools to use in the OpenAI API call.
        **call_params: The `OpenAICallParams` call parameters to use in the API call.

    Returns:
        The decorator for turning a typed function into an AsyncOpenAI API call.
    '''
    if stream and output_parser:
        raise ValueError("Using both `stream` and `output_parser` not supported yet.")
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
            stream_async_decorator, model=model, tools=tools, call_params=call_params
        )
    return partial(
        create_async_decorator,
        model=model,
        tools=tools,
        output_parser=output_parser,
        call_params=call_params,
    )
