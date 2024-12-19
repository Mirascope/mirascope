"""This module defines the base class for structured streams."""

from collections.abc import (
    AsyncGenerator,
    AsyncIterable,
    Awaitable,
    Callable,
    Generator,
    Iterable,
)
from functools import wraps
from typing import (
    Any,
    Generic,
    ParamSpec,
    TypeVar,
    cast,
    overload,
)

from pydantic import BaseModel

from ._utils import (
    BaseType,
    GetJsonOutput,
    SameSyncAndAsyncClientSetupCall,
    SetupCall,
    extract_tool_return,
    fn_is_async,
    setup_extract_tool,
)
from ._utils._get_fields_from_call_args import (
    get_fields_from_call_args,
)
from .call_params import BaseCallParams
from .call_response import BaseCallResponse
from .call_response_chunk import BaseCallResponseChunk
from .dynamic_config import BaseDynamicConfig
from .stream import BaseStream, stream_factory
from .tool import BaseTool

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)


class BaseStructuredStream(Generic[_ResponseModelT]):
    """A base class for streaming structured outputs from LLMs."""

    stream: BaseStream
    response_model: type[_ResponseModelT]
    constructed_response_model: _ResponseModelT

    def __init__(
        self,
        *,
        stream: BaseStream,
        response_model: type[_ResponseModelT],
        fields_from_call_args: dict[str, Any],
    ) -> None:
        """Initializes an instance of `BaseStructuredStream`."""
        self.stream = stream
        self.response_model = response_model
        self.fields_from_call_args = fields_from_call_args

    def __iter__(self) -> Generator[_ResponseModelT, None, None]:
        """Iterates over the stream and extracts structured outputs."""
        json_output = ""
        for chunk, _ in self.stream:
            json_output += chunk.content
            if json_output and json_output[0] != "{":
                try:
                    json_start = json_output.index("{")
                    json_output = json_output[json_start:]
                except ValueError:
                    json_output = ""
            if chunk.model is not None:
                self.stream.model = chunk.model
            if json_output:
                yield extract_tool_return(
                    self.response_model, json_output, True, self.fields_from_call_args
                )
        if json_output:
            json_output = json_output[: json_output.rfind("}") + 1]
        self.constructed_response_model = extract_tool_return(
            self.response_model, json_output, False, self.fields_from_call_args
        )
        yield self.constructed_response_model

    def __aiter__(self) -> AsyncGenerator[_ResponseModelT, None]:
        """Iterates over the stream and extracts structured outputs."""

        async def generator() -> AsyncGenerator[_ResponseModelT, None]:
            json_output = ""
            async for chunk, _ in self.stream:
                json_output += chunk.content
                if json_output and json_output[0] != "{":
                    try:
                        json_start = json_output.index("{")
                        json_output = json_output[json_start:]
                    except ValueError:
                        json_output = ""
                if chunk.model is not None:
                    self.stream.model = chunk.model
                if json_output:
                    yield extract_tool_return(
                        self.response_model,
                        json_output,
                        True,
                        self.fields_from_call_args,
                    )
            if json_output:
                json_output = json_output[: json_output.rfind("}") + 1]
            self.constructed_response_model = extract_tool_return(
                self.response_model, json_output, False, self.fields_from_call_args
            )
            yield self.constructed_response_model

        return generator()


_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", bound=BaseDynamicConfig)
_SameSyncAndAsyncClientT = TypeVar("_SameSyncAndAsyncClientT", contravariant=True)
_SyncBaseClientT = TypeVar("_SyncBaseClientT", contravariant=True)
_AsyncBaseClientT = TypeVar("_AsyncBaseClientT", contravariant=True)
_ResponseT = TypeVar("_ResponseT")
_ResponseChunkT = TypeVar("_ResponseChunkT")
_AsyncResponseT = TypeVar("_AsyncResponseT")
_AsyncResponseChunkT = TypeVar("_AsyncResponseChunkT")
_P = ParamSpec("_P")


def structured_stream_factory(  # noqa: ANN201
    *,
    TCallResponse: type[_BaseCallResponseT],
    TCallResponseChunk: type[_BaseCallResponseChunkT],
    TStream: type[BaseStream],
    TToolType: type[_BaseToolT],
    setup_call: SameSyncAndAsyncClientSetupCall[
        _SameSyncAndAsyncClientT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _BaseCallParamsT,
        _ResponseT,
        _ResponseChunkT,
        _AsyncResponseT,
        _AsyncResponseChunkT,
        _BaseToolT,
    ]
    | SetupCall[
        _SyncBaseClientT,
        _AsyncBaseClientT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _BaseCallParamsT,
        _ResponseT,
        _ResponseChunkT,
        _AsyncResponseT,
        _AsyncResponseChunkT,
        _BaseToolT,
    ],
    get_json_output: GetJsonOutput[_BaseCallResponseChunkT],
):
    class CustomContentChunk(TCallResponseChunk):
        json_output: str

        @property
        def content(self) -> str:
            return self.json_output

    @overload
    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _SameSyncAndAsyncClientT | _SyncBaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        Iterable[_ResponseModelT],
    ]: ...

    @overload
    def decorator(
        fn: Callable[_P, Awaitable[_AsyncBaseDynamicConfigT]],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _SameSyncAndAsyncClientT | _AsyncBaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        Awaitable[AsyncIterable[_ResponseModelT]],
    ]: ...

    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT]
        | Callable[_P, Awaitable[_AsyncBaseDynamicConfigT]],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _SameSyncAndAsyncClientT | _SyncBaseClientT | _AsyncBaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        Iterable[_ResponseModelT] | Awaitable[AsyncIterable[_ResponseModelT]],
    ]:
        def handle_chunk(
            chunk: _ResponseChunkT | _AsyncResponseChunkT,
        ) -> tuple[_BaseCallResponseChunkT, None]:
            call_response_chunk = TCallResponseChunk(chunk=chunk)
            json_output = get_json_output(call_response_chunk, json_mode)

            call_response_chunk = cast(
                _BaseCallResponseChunkT,
                CustomContentChunk(chunk=chunk, json_output=json_output),  # pyright: ignore [reportAbstractUsage]
            )
            return call_response_chunk, None

        def handle_stream(
            stream: Generator[_ResponseChunkT, None, None],
            tool_types: list[type[_BaseToolT]] | None,
            partial_tools: bool = False,
        ) -> Generator[tuple[_BaseCallResponseChunkT, None], None, None]:
            for chunk in stream:
                yield handle_chunk(chunk)

        async def handle_stream_async(
            stream: AsyncGenerator[_AsyncResponseChunkT, None],
            tool_types: list[type[_BaseToolT]] | None,
            partial_tools: bool = False,
        ) -> AsyncGenerator[tuple[_BaseCallResponseChunkT, None], None]:
            async for chunk in stream:
                yield handle_chunk(chunk)

        stream_decorator = stream_factory(
            TCallResponse=TCallResponse,
            TStream=TStream,
            setup_call=setup_call,
            handle_stream=handle_stream,
            handle_stream_async=handle_stream_async,
        )

        tool = setup_extract_tool(response_model, TToolType)
        stream_decorator_kwargs = {
            "model": model,
            "tools": [tool],
            "json_mode": json_mode,
            "client": client,
            "call_params": call_params,
        }
        fn._model = model  # pyright: ignore [reportFunctionMemberAccess]
        fn.__mirascope_call__ = True  # pyright: ignore [reportFunctionMemberAccess]
        if fn_is_async(fn):

            @wraps(fn)
            async def inner_async(
                *args: _P.args, **kwargs: _P.kwargs
            ) -> AsyncIterable[_ResponseModelT]:
                fields_from_call_args = get_fields_from_call_args(
                    response_model, fn, args, kwargs
                )
                return BaseStructuredStream[_ResponseModelT](
                    stream=await stream_decorator(fn=fn, **stream_decorator_kwargs)(
                        *args, **kwargs
                    ),
                    response_model=response_model,
                    fields_from_call_args=fields_from_call_args,
                )

            return inner_async
        else:

            @wraps(fn)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> Iterable[_ResponseModelT]:
                fields_from_call_args = get_fields_from_call_args(
                    response_model, fn, args, kwargs
                )
                return BaseStructuredStream[_ResponseModelT](
                    stream=stream_decorator(fn=fn, **stream_decorator_kwargs)(
                        *args, **kwargs
                    ),
                    response_model=response_model,
                    fields_from_call_args=fields_from_call_args,
                )

            return inner

    return decorator
