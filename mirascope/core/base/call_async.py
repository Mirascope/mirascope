"""The `call_async_factory` method for generating provider specific call decorators."""

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

from ._utils import BaseType
from .call_response import BaseCallResponse
from .call_response_chunk import BaseCallResponseChunk
from .dynamic_config import BaseDynamicConfig
from .stream_async import BaseAsyncStream
from .tool import BaseTool

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)
_ExtractModelT = TypeVar("_ExtractModelT", bound=BaseModel | BaseType)
_ParsedOutputT = TypeVar("_ParsedOutputT")
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseModel)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseAsyncStreamT = TypeVar("_BaseAsyncStreamT", bound=BaseAsyncStream)
_P = ParamSpec("_P")


def call_async_factory(
    TCallResponse: type[_BaseCallResponseT],
    TCallResponseChunk: type[_BaseCallResponseChunkT],
    TCallParams: type[_BaseCallParamsT],
    TFunctionReturn: type[_BaseDynamicConfigT],
    TAsyncStream: type[_BaseAsyncStreamT],
    create_async_decorator: Callable[
        [
            Callable[_P, Awaitable[_BaseDynamicConfigT]],
            str,
            list[type[BaseTool] | Callable] | None,
            Callable[[_BaseCallResponseT], _ParsedOutputT] | None,
            _BaseCallParamsT,
        ],
        Callable[_P, Awaitable[_BaseCallResponseT | _ParsedOutputT]],
    ],
    stream_async_decorator: Callable[
        [
            Callable[_P, Awaitable[_BaseDynamicConfigT]],
            str,
            list[type[BaseTool] | Callable] | None,
            Callable[[_BaseCallResponseChunkT], _ParsedOutputT] | None,
            _BaseCallParamsT,
        ],
        Callable[_P, Awaitable[_BaseAsyncStreamT]],
    ],
    extract_async_decorator: Callable[
        [
            Callable[_P, Awaitable[_BaseDynamicConfigT]],
            str,
            type[_ExtractModelT],
            _BaseCallParamsT,
        ],
        Callable[_P, Awaitable[_ExtractModelT]],
    ],
    structured_stream_async_decorator: Callable[
        [
            Callable[_P, Awaitable[_BaseDynamicConfigT]],
            str,
            type[_ExtractModelT],
            _BaseCallParamsT,
        ],
        Callable[_P, Awaitable[AsyncIterable[_ExtractModelT]]],
    ],
):
    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, Awaitable[TFunctionReturn]]],
        Callable[_P, Awaitable[TCallResponse]],
    ]: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[TCallResponse], _ParsedOutputT],
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, Awaitable[TFunctionReturn]]],
        Callable[_P, Awaitable[_ParsedOutputT]],
    ]: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[TCallResponseChunk], _ParsedOutputT],
        **call_params: Unpack[TCallParams],
    ) -> NoReturn: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[True] = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, Awaitable[TFunctionReturn]]],
        Callable[_P, Awaitable[TAsyncStream]],
    ]: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[True] = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[TCallResponseChunk], _ParsedOutputT],
        **call_params: Unpack[TCallParams],
    ) -> NoReturn: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[True] = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[TCallResponse], _ParsedOutputT],
        **call_params: Unpack[TCallParams],
    ) -> NoReturn: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, Awaitable[TFunctionReturn]]],
        Callable[_P, Awaitable[_ResponseModelT]],
    ]: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[TCallResponse], _ParsedOutputT]
        | Callable[[TCallResponseChunk], _ParsedOutputT],
        **call_params: Unpack[TCallParams],
    ) -> NoReturn: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[True],
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, Awaitable[TFunctionReturn]]],
        Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]],
    ]: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[True],
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[TCallResponse], _ParsedOutputT]
        | Callable[[TCallResponseChunk], _ParsedOutputT],
        **call_params: Unpack[TCallParams],
    ) -> NoReturn: ...  # pragma: no cover

    def base_call(
        model: str,
        *,
        stream: bool = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT] | None = None,
        output_parser: Callable[[TCallResponse], _ParsedOutputT]
        | Callable[[TCallResponseChunk], _ParsedOutputT]
        | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, Awaitable[TFunctionReturn]]],
        Callable[
            _P,
            Awaitable[TCallResponse]
            | Awaitable[_ParsedOutputT]
            | Awaitable[TAsyncStream]
            | Awaitable[_ResponseModelT]
            | Awaitable[AsyncIterable[_ResponseModelT]],
        ],
    ]:
        if stream and output_parser:
            raise ValueError("Cannot use `output_parser` with `stream=True`.")
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
                call_params=call_params,
            )
        return partial(
            create_async_decorator,
            model=model,
            tools=tools,
            output_parser=output_parser,  # type: ignore
            call_params=call_params,
        )

    return base_call
