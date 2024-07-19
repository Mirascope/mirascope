"""This module defines the base class for structured streams."""

import inspect
from collections.abc import AsyncGenerator, Generator
from functools import wraps
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

from ._stream import BaseStream
from ._utils import (
    BaseType,
    GetJsonOutput,
    SetupCall,
    extract_tool_return,
    get_fn_args,
    get_metadata,
    setup_extract_tool,
)
from .call_params import BaseCallParams
from .call_response import BaseCallResponse
from .call_response_chunk import BaseCallResponseChunk
from .dynamic_config import BaseDynamicConfig
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
        stream: BaseStream,
        *,
        response_model: type[_ResponseModelT],
    ):
        """Initializes an instance of `BaseStructuredStream`."""
        self.stream = stream
        self.response_model = response_model

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
                yield extract_tool_return(self.response_model, json_output, True)
        if json_output:
            json_output = json_output[: json_output.rfind("}") + 1]
        extracted_response_model = extract_tool_return(
            self.response_model, json_output, False
        )
        self.constructed_response_model = extracted_response_model
        yield extracted_response_model

    def __aiter__(self) -> AsyncGenerator[_ResponseModelT, None]:
        """Iterates over the stream and extracts structured outputs."""

        async def generator():
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
                    yield extract_tool_return(self.response_model, json_output, True)
            if json_output:
                json_output = json_output[: json_output.rfind("}") + 1]
            extracted_response_model = extract_tool_return(
                self.response_model, json_output, False
            )
            self.constructed_response_model = extracted_response_model
            yield extracted_response_model

        return generator()


_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseClientT = TypeVar("_BaseClientT", bound=object)
_ResponseT = TypeVar("_ResponseT")
_ResponseChunkT = TypeVar("_ResponseChunkT")
_P = ParamSpec("_P")


def structured_stream_factory(
    *,
    TCallResponse: type[_BaseCallResponseT],
    TCallResponseChunk: type[_BaseCallResponseChunkT],
    TStream: type[BaseStream],
    TToolType: type[_BaseToolT],
    setup_call: SetupCall[
        _BaseClientT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
        _ResponseT,
        _ResponseChunkT,
        _BaseToolT,
    ],
    get_json_output: GetJsonOutput[_BaseCallResponseChunkT],
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
            create, prompt_template, messages, tool_types, call_kwargs = setup_call(
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

            def generator():
                for chunk in create(stream=True, **call_kwargs):
                    call_response_chunk = TCallResponseChunk(chunk=chunk)
                    json_output = get_json_output(call_response_chunk, json_mode)
                    call_response_chunk_type = type(call_response_chunk)
                    setattr(call_response_chunk_type, "content", json_output)
                    yield call_response_chunk_type(chunk=chunk), None

            stream = TStream(
                generator(),
                metadata=get_metadata(fn, dynamic_config),
                tool_types=tool_types,
                call_response_type=TCallResponse,
                model=model,
                prompt_template=prompt_template,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                messages=messages,
                call_params=call_params,
            )

            return BaseStructuredStream[_ResponseModelT](
                stream,
                response_model=response_model,
            )

        async def inner_async(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> AsyncIterable[_ResponseModelT]:
            assert SetupCall.fn_is_async(fn)
            fn_args = get_fn_args(fn, args, kwargs)
            dynamic_config = await fn(*args, **kwargs)
            create, prompt_template, messages, tool_types, call_kwargs = setup_call(
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

            async def generator():
                async for chunk in await create(stream=True, **call_kwargs):
                    call_response_chunk = TCallResponseChunk(chunk=chunk)
                    json_output = get_json_output(call_response_chunk, json_mode)
                    call_response_chunk_type = type(call_response_chunk)
                    setattr(call_response_chunk_type, "content", json_output)
                    yield call_response_chunk_type(chunk=chunk), None

            stream = TStream(
                generator(),
                metadata=get_metadata(fn, dynamic_config),
                tool_types=tool_types,
                call_response_type=TCallResponse,
                model=model,
                prompt_template=prompt_template,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                messages=messages,
                call_params=call_params,
            )

            return BaseStructuredStream[_ResponseModelT](
                stream,
                response_model=response_model,
            )

        return inner_async if is_async else inner

    return decorator
