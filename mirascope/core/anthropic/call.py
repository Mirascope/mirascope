"""The `anthropic_call` decorator for functions as LLM calls."""

from functools import partial
from typing import (
    Callable,
    Iterable,
    Literal,
    NoReturn,
    ParamSpec,
    TypeVar,
    Unpack,
    overload,
)

from pydantic import BaseModel

from ..base import BaseTool, _utils
from ._create import create_decorator
from ._extract import extract_decorator
from ._stream import AnthropicStream, stream_decorator
from ._structured_stream import structured_stream_decorator
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .call_response_chunk import AnthropicCallResponseChunk
from .function_return import AnthropicCallFunctionReturn

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)
_ParsedOutputT = TypeVar("_ParsedOutputT")


@overload
def anthropic_call(
    model: str,
    max_tokens: int = 1000,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, AnthropicCallFunctionReturn]],
    Callable[_P, AnthropicCallResponse],
]: ...  # pragma: no cover


@overload
def anthropic_call(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: Callable[[AnthropicCallResponse], _ParsedOutputT],
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, AnthropicCallFunctionReturn]],
    Callable[_P, _ParsedOutputT],
]: ...  # pragma: no cover


@overload
def anthropic_call(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: Callable[[AnthropicCallResponseChunk], _ParsedOutputT],
    **call_params: Unpack[AnthropicCallParams],
) -> NoReturn: ...  # pragma: no cover


@overload
def anthropic_call(
    model: str,
    *,
    stream: Literal[True] = True,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, AnthropicCallFunctionReturn]],
    Callable[_P, AnthropicStream[AnthropicCallResponseChunk]],
]: ...  # pragma: no cover


@overload
def anthropic_call(
    model: str,
    *,
    stream: Literal[True] = True,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: Callable[[AnthropicCallResponseChunk], _ParsedOutputT],
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, AnthropicCallFunctionReturn]],
    Callable[_P, AnthropicStream[_ParsedOutputT]],
]: ...  # pragma: no cover


@overload
def anthropic_call(
    model: str,
    *,
    stream: Literal[True] = True,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: Callable[[AnthropicCallResponse], _ParsedOutputT],
    **call_params: Unpack[AnthropicCallParams],
) -> NoReturn: ...  # pragma: no cover


@overload
def anthropic_call(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, AnthropicCallFunctionReturn]],
    Callable[_P, _ResponseModelT],
]: ...  # pragma: no cover


@overload
def anthropic_call(
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
def anthropic_call(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    **call_params: Unpack[AnthropicCallParams],
) -> Callable[
    [Callable[_P, AnthropicCallFunctionReturn]],
    Callable[_P, Iterable[_ResponseModelT]],
]: ...  # pragma: no cover


@overload
def anthropic_call(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: Callable[[AnthropicCallResponse], _ParsedOutputT]
    | Callable[[AnthropicCallResponseChunk], _ParsedOutputT],
    **call_params: Unpack[AnthropicCallParams],
) -> NoReturn: ...  # pragma: no cover


def anthropic_call(
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
    [Callable[_P, AnthropicCallFunctionReturn]],
    Callable[
        _P,
        AnthropicCallResponse
        | _ParsedOutputT
        | AnthropicStream[AnthropicCallResponseChunk | _ParsedOutputT]
        | _ResponseModelT
        | Iterable[_ResponseModelT],
    ],
]:
    '''A decorator for calling the Anthropic API with a typed function.

    This decorator is used to wrap a typed function that calls the Anthropic API. It
    parses the docstring of the wrapped function as the messages array and templates the
    input arguments for the function into each message's template.

    Example:

    ```python
    @anthropic_call(model="claude-3-5-sonnet-20240620")
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    response = recommend_book("fantasy")
    ```

    Args:
        model: The Anthropic model to use in the API call.
        stream: Whether to stream the response from the API call.
        tools: The tools to use in the Anthropic API call.
        **call_params: The `AnthropicCallParams` call parameters to use in the API call.

    Returns:
        The decorator for turning a typed function into an Anthropic API call.
    '''
    if response_model and output_parser:
        raise ValueError("Cannot use both `response_model` and `output_parser`.")

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
            stream_decorator,
            model=model,
            tools=tools,
            output_parser=output_parser,  # type: ignore
            call_params=call_params,
        )
    return partial(
        create_decorator,
        model=model,
        tools=tools,
        output_parser=output_parser,  # type: ignore
        call_params=call_params,
    )
