"""The `anthropic_call_async` decorator for easy Anthropic API typed functions."""

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

from mirascope.core.anthropic.call_response_chunk import AnthropicCallResponseChunk

from ..base import BaseTool, _utils
from ._create_async import create_async_decorator
from ._extract_async import extract_async_decorator
from ._stream_async import AnthropicAsyncStream, stream_async_decorator
from ._structured_stream_async import structured_stream_async_decorator
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .function_return import AnthropicCallFunctionReturn

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)
_ParsedOutputT = TypeVar("_ParsedOutputT")


@overload
def anthropic_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, Awaitable[AnthropicCallFunctionReturn]]],
    Callable[_P, Awaitable[AnthropicCallResponse]],
]: ...  # pragma: no cover


@overload
def anthropic_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: Callable[[AnthropicCallResponse], _ParsedOutputT],
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, Awaitable[AnthropicCallFunctionReturn]]],
    Callable[_P, Awaitable[_ParsedOutputT]],
]: ...  # pragma: no cover


@overload
def anthropic_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: Callable[[AnthropicCallResponseChunk], _ParsedOutputT],
    **call_params: Unpack[AnthropicCallParams],
) -> NoReturn: ...  # pragma: no cover


@overload
def anthropic_call_async(
    model: str,
    *,
    stream: Literal[True] = True,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, Awaitable[AnthropicCallFunctionReturn]]],
    Callable[_P, Awaitable[AnthropicAsyncStream[AnthropicCallResponseChunk]]],
]: ...  # pragma: no cover


@overload
def anthropic_call_async(
    model: str,
    *,
    stream: Literal[True] = True,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: Callable[[AnthropicCallResponseChunk], _ParsedOutputT],
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, Awaitable[AnthropicCallFunctionReturn]]],
    Callable[_P, Awaitable[AnthropicAsyncStream[_ParsedOutputT]]],
]: ...  # pragma: no cover


@overload
def anthropic_call_async(
    model: str,
    *,
    stream: Literal[True] = True,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: Callable[[AnthropicCallResponse], _ParsedOutputT],
    **call_params: Unpack[AnthropicCallParams],
) -> NoReturn: ...  # pragma: no cover


@overload
def anthropic_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, Awaitable[AnthropicCallFunctionReturn]]],
    Callable[_P, Awaitable[_ResponseModelT]],
]: ...  # pragma: no cover


@overload
def anthropic_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: Callable[[AnthropicCallResponse], _ParsedOutputT]
    | Callable[[AnthropicCallResponseChunk], _ParsedOutputT],
    **call_params: Unpack[AnthropicCallParams],
) -> NoReturn: ...  # pragma: no cover


@overload
def anthropic_call_async(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, Awaitable[AnthropicCallFunctionReturn]]],
    Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]],
]: ...  # pragma: no cover


@overload
def anthropic_call_async(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: Callable[[AnthropicCallResponse], _ParsedOutputT]
    | Callable[[AnthropicCallResponseChunk], _ParsedOutputT],
    **call_params: Unpack[AnthropicCallParams],
) -> NoReturn: ...  # pragma: no cover


def anthropic_call_async(
    model: str,
    *,
    stream: bool = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[AnthropicCallResponse], _ParsedOutputT]
    | Callable[[AnthropicCallResponseChunk], _ParsedOutputT]
    | None = None,
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, Awaitable[AnthropicCallFunctionReturn]]],
    Callable[
        _P,
        Awaitable[AnthropicCallResponse | _ParsedOutputT]
        | Awaitable[AnthropicAsyncStream[AnthropicCallResponseChunk | _ParsedOutputT]]
        | Awaitable[_ResponseModelT]
        | Awaitable[AsyncIterable[_ResponseModelT]],
    ],
]:
    '''A decorator for calling the AsyncAnthropic API with a typed function.

    This decorator is used to wrap a typed function that calls the Anthropic API. It parses
    the docstring of the wrapped function as the messages array and templates the input
    arguments for the function into each message's template.

    Example:

    ```python
    @anthropic_call_async(model="claude-3-5-sonnet-20240620")
    async def recommend_book(genre: str):
        """Recommend a {genre} book."""

    async def run():
        response = await recommend_book("fantasy")

    asyncio.run(run())
    ```

    Args:
        model: The Anthropic model to use in the API call.
        stream: Whether to stream the response from the API call.
        tools: The tools to use in the Anthropic API call.
        **call_params: The `AnthropicCallParams` call parameters to use in the API call.

    Returns:
        The decorator for turning a typed function into an AsyncAnthropic API call.
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
            output_parser=output_parser,  # type: ignore
            call_params=call_params,
        )
    return partial(
        create_async_decorator,
        model=model,
        tools=tools,
        output_parser=output_parser,  # type: ignore
        call_params=call_params,
    )
