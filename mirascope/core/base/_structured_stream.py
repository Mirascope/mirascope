"""This module defines the base class for structured streams."""

import inspect
from collections.abc import AsyncGenerator, Generator
from functools import wraps
from re import T
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Generic,
    Iterable,
    ParamSpec,
    TypeVar,
    overload,
)

from pydantic import BaseModel

from ._utils import (
    BaseType,
    GetJsonOutput,
    SetupCall,
    extract_tool_return,
    get_fn_args,
    setup_extract_tool,
)
from .call_params import BaseCallParams
from .call_response_chunk import BaseCallResponseChunk
from .dynamic_config import BaseDynamicConfig
from .tool import BaseTool

_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_AssistantMessageParamT = TypeVar("_AssistantMessageParamT")
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)


class BaseStructuredStream(Generic[_BaseCallResponseChunkT, _ResponseModelT]):
    """A base class for streaming structured outputs from LLMs."""

    stream: (
        Generator[_BaseCallResponseChunkT, None, None]
        | AsyncGenerator[_BaseCallResponseChunkT, None]
    )
    response_model: type[_ResponseModelT]
    json_mode: bool
    get_json_output: GetJsonOutput[_BaseCallResponseChunkT]

    def __init__(
        self,
        stream: Generator[_BaseCallResponseChunkT, None, None]
        | AsyncGenerator[_BaseCallResponseChunkT, None],
        *,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        get_json_output: Callable,
    ):
        """Initializes an instance of `BaseStructuredStream`."""
        self.stream = stream
        self.response_model = response_model
        self.json_mode = json_mode
        self.get_json_output = get_json_output

    def __iter__(self) -> Generator[_ResponseModelT, None, None]:
        """Iterates over the stream and extracts structured outputs."""
        assert isinstance(
            self.stream, Generator
        ), "Stream must be a generator for __iter__"
        json_output = ""
        for chunk in self.stream:
            json_output += self.get_json_output(chunk, self.json_mode)
            if json_output and json_output[0] != "{":
                try:
                    json_start = json_output.index("{")
                    json_output = json_output[json_start:]
                except ValueError:
                    json_output = ""
            if chunk.model is not None:
                self.model = chunk.model
            if json_output:
                yield extract_tool_return(self.response_model, json_output, True)
        if json_output:
            json_output = json_output[: json_output.rfind("}") + 1]
        yield extract_tool_return(self.response_model, json_output, False)

    def __aiter__(self) -> AsyncGenerator[_ResponseModelT, None]:
        """Iterates over the stream and extracts structured outputs."""

        async def generator():
            assert isinstance(
                self.stream, AsyncGenerator
            ), "Stream must be an async generator for __aiter__"
            json_output = ""
            async for chunk in self.stream:
                json_output += self.get_json_output(chunk, self.json_mode)
                if json_output and json_output[0] != "{":
                    try:
                        json_start = json_output.index("{")
                        json_output = json_output[json_start:]
                    except ValueError:
                        json_output = ""
                if chunk.model is not None:
                    self.model = chunk.model
                if json_output:
                    yield extract_tool_return(self.response_model, json_output, True)
            if json_output:
                json_output = json_output[: json_output.rfind("}") + 1]
            yield extract_tool_return(self.response_model, json_output, False)

        return generator()


_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseClientT = TypeVar("_BaseClientT", bound=object)
_ResponseT = TypeVar("_ResponseT")
_ResponseChunkT = TypeVar("_ResponseChunkT")
_P = ParamSpec("_P")


def structured_stream_factory(
    *,
    TCallResponseChunk: type[_BaseCallResponseChunkT],
    TToolType: type[_BaseToolT],
    setup_call: SetupCall[
        _BaseClientT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
        _ResponseT,
        _ResponseChunkT,
        _BaseToolT,
    ],
    get_json_output: GetJsonOutput[_ResponseT],
):
    @overload
    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        Iterable[_ResponseModelT],
    ]: ...  # pragma: no cover

    @overload
    def decorator(
        fn: Callable[_P, Awaitable[_BaseDynamicConfigT]],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        Awaitable[AsyncIterable[_ResponseModelT]],
    ]: ...  # pragma: no cover

    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        Iterable[_ResponseModelT] | Awaitable[AsyncIterable[_ResponseModelT]],
    ]:
        tool = setup_extract_tool(response_model, TToolType)
        is_async = inspect.iscoroutinefunction(fn)

        @wraps(fn)
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> Iterable[_ResponseModelT]:
            assert SetupCall.fn_is_sync(fn)
            fn_args = get_fn_args(fn, args, kwargs)
            dynamic_config = fn(*args, **kwargs)
            create, _, _, _, call_kwargs = setup_call(
                model=model,
                client=client,
                fn=fn,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                tools=[tool],
                json_mode=json_mode,
                call_params=call_params,
                extract=True,
            )
            stream = create(stream=True, **call_kwargs)
            return BaseStructuredStream[_BaseCallResponseChunkT, _ResponseModelT](
                (TCallResponseChunk(chunk=chunk) for chunk in stream),
                response_model=response_model,
                json_mode=json_mode,
                get_json_output=get_json_output,
            )

        async def inner_async(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> AsyncIterable[_ResponseModelT]:
            assert SetupCall.fn_is_async(fn)
            fn_args = get_fn_args(fn, args, kwargs)
            dynamic_config = await fn(*args, **kwargs)
            create, _, _, _, call_kwargs = setup_call(
                model=model,
                client=client,
                fn=fn,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                tools=[tool],
                json_mode=json_mode,
                call_params=call_params,
                extract=True,
            )
            stream = await create(stream=True, **call_kwargs)
            return BaseStructuredStream[_BaseCallResponseChunkT, _ResponseModelT](
                (TCallResponseChunk(chunk=chunk) async for chunk in stream),
                response_model=response_model,
                json_mode=json_mode,
                get_json_output=get_json_output,
            )

        return inner_async if is_async else inner

    return decorator
