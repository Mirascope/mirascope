"""The `call_factory` method for generating provider specific call decorators."""

from collections.abc import AsyncGenerator, Generator
from functools import partial
from typing import (
    Any,
    Awaitable,
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

from ._create import create_factory
from ._extract import extract_factory
from ._stream import BaseStream, stream_factory
from ._utils import BaseType
from .call_response import BaseCallResponse
from .call_response_chunk import BaseCallResponseChunk
from .dynamic_config import BaseDynamicConfig
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
_BaseStreamT = TypeVar("_BaseStreamT", bound=BaseStream)
_BaseClientT = TypeVar("_BaseClientT", bound=object)
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ResponseT = TypeVar("_ResponseT")
_AssistantMessageParamT = TypeVar("_AssistantMessageParamT")
_P = ParamSpec("_P")


def call_factory(
    *,
    TCallResponse: type[_BaseCallResponseT],
    TCallResponseChunk: type[_BaseCallResponseChunkT],
    TCallParams: type[_BaseCallParamsT],
    TDynamicConfig: type[_BaseDynamicConfigT],
    TStream: type[_BaseStreamT],
    TMessageParamType: type[_AssistantMessageParamT],
    TToolType: type[_BaseToolT],
    setup_call: Callable[
        [
            str,
            _BaseClientT,
            Callable[_P, _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
            dict[str, Any],
            _BaseDynamicConfigT,
            list[type[BaseTool] | Callable] | None,
            _BaseCallParamsT,
            bool,
        ],
        tuple[
            Callable[..., _ResponseT],
            str,
            list[dict[str, Any]],
            list[type[BaseTool]],
            dict[str, Any],
        ],
    ],
    get_json_output: Callable[[_ResponseT, bool], str],
    handle_stream: Callable[
        [Generator[_BaseCallResponseChunkT, None, None], list[type[_BaseToolT]]],
        Generator[tuple[_BaseCallResponseChunkT, _BaseToolT], None, None],
    ],
    handle_stream_async: Callable[
        [AsyncGenerator[_BaseCallResponseChunkT, None], list[type[_BaseToolT]]],
        Awaitable[AsyncGenerator[tuple[_BaseCallResponseChunkT, _BaseToolT], None]],
    ],
    calculate_cost: Callable[[_ResponseT, str], float],
    structured_stream_decorator: Callable[
        [
            Callable[_P, _BaseDynamicConfigT],
            str,
            type[_ExtractModelT],
            _BaseClientT,
            _BaseCallParamsT,
        ],
        Callable[_P, Iterable[_ExtractModelT]],
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
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TDynamicConfig]],
        Callable[_P, TCallResponse],
    ]: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[TCallResponse], _ParsedOutputT],
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TDynamicConfig]],
        Callable[_P, _ParsedOutputT],
    ]: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[TCallResponseChunk], _ParsedOutputT],
        json_mode: bool = False,
        client: _BaseClientT | None = None,
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
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TDynamicConfig]],
        Callable[_P, TStream],
    ]: ...  # pragma: no cover

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[True] = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[TCallResponseChunk], _ParsedOutputT],
        json_mode: bool = False,
        client: _BaseClientT | None = None,
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
        json_mode: bool = False,
        client: _BaseClientT | None = None,
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
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TDynamicConfig]],
        Callable[_P, _ResponseModelT],
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
        json_mode: bool = False,
        client: _BaseClientT | None = None,
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
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TDynamicConfig]],
        Callable[_P, Iterable[_ResponseModelT]],
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
        json_mode: bool = False,
        client: _BaseClientT | None = None,
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
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TDynamicConfig]],
        Callable[
            _P,
            TCallResponse
            | _ParsedOutputT
            | TStream
            | _ResponseModelT
            | Iterable[_ResponseModelT],
        ],
    ]:
        if stream and output_parser:
            raise ValueError("Cannot use `output_parser` with `stream=True`.")
        if response_model and output_parser:
            raise ValueError("Cannot use both `response_model` and `output_parser`.")

        if response_model:
            if stream:
                return partial(
                    structured_stream_decorator,
                    model=model,
                    response_model=response_model,
                    client=client,
                    call_params=call_params,
                )
            else:
                return partial(
                    extract_factory(
                        TCallResponse=TCallResponse,
                        TToolType=TToolType,
                        setup_call=setup_call,
                        get_json_output=get_json_output,
                        calculate_cost=calculate_cost,
                    ),
                    model=model,
                    response_model=response_model,
                    json_mode=json_mode,
                    client=client,
                    call_params=call_params,
                )
        if stream:
            return partial(
                stream_factory(
                    TCallResponseChunk=TCallResponseChunk,
                    TStream=TStream,
                    TMessageParamType=TMessageParamType,
                    setup_call=setup_call,
                    handle_stream=handle_stream,
                    handle_stream_async=handle_stream_async,
                ),
                model=model,
                tools=tools,
                json_mode=json_mode,
                client=client,
                call_params=call_params,
            )
        return partial(
            create_factory(
                TCallResponse=TCallResponse,
                setup_call=setup_call,
                calculate_cost=calculate_cost,
            ),
            model=model,
            tools=tools,
            output_parser=output_parser,
            json_mode=json_mode,
            client=client,
            call_params=call_params,
        )

    return base_call
