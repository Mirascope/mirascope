"""The `call_factory` method for generating provider specific call decorators."""

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

from ._utils import BaseType
from .call_response import BaseCallResponse
from .call_response_chunk import BaseCallResponseChunk
from .dynamic_config import BaseDynamicConfig
from .stream import BaseStream
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
_P = ParamSpec("_P")


def call_factory(
    TCallResponse: type[_BaseCallResponseT],
    TCallResponseChunk: type[_BaseCallResponseChunkT],
    TCallParams: type[_BaseCallParamsT],
    TFunctionReturn: type[_BaseDynamicConfigT],
    TStream: type[_BaseStreamT],
    create_decorator: Callable[
        [
            Callable[_P, _BaseDynamicConfigT],
            str,
            list[type[BaseTool] | Callable] | None,
            Callable[[_BaseCallResponseT], _ParsedOutputT] | None,
            _BaseClientT,
            _BaseCallParamsT,
        ],
        Callable[_P, _BaseCallResponseT | _ParsedOutputT],
    ],
    stream_decorator: Callable[
        [
            Callable[_P, _BaseDynamicConfigT],
            str,
            list[type[BaseTool] | Callable] | None,
            Callable[[_BaseCallResponseChunkT], _ParsedOutputT] | None,
            _BaseClientT,
            _BaseCallParamsT,
        ],
        Callable[_P, _BaseStreamT],
    ],
    extract_decorator: Callable[
        [
            Callable[_P, _BaseDynamicConfigT],
            str,
            type[_ExtractModelT],
            _BaseClientT,
            _BaseCallParamsT,
        ],
        Callable[_P, _ExtractModelT],
    ],
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
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TFunctionReturn]],
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
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TFunctionReturn]],
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
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TFunctionReturn]],
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
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TFunctionReturn]],
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
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TFunctionReturn]],
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
        client: _BaseClientT | None = None,
        **call_params: Unpack[TCallParams],
    ) -> Callable[
        [Callable[_P, TFunctionReturn]],
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
                    extract_decorator,
                    model=model,
                    response_model=response_model,
                    client=client,
                    call_params=call_params,
                )
        if stream:
            return partial(
                stream_decorator,
                model=model,
                tools=tools,
                client=client,
                call_params=call_params,
            )
        return partial(
            create_decorator,
            model=model,
            tools=tools,
            output_parser=output_parser,  # type: ignore
            client=client,
            call_params=call_params,
        )

    return base_call
