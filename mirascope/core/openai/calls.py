"""The `openai_call` decorator for easy OpenAI API typed functions."""

import datetime
import inspect
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    Literal,
    ParamSpec,
    TypeVar,
    Unpack,
    overload,
)

from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

from ..base import BaseTool
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .function_return import OpenAICallFunctionReturn
from .streams import OpenAIAsyncStream, OpenAIStream
from .utils import setup_call

P = ParamSpec("P")
ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)


@overload
def openai_call(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[P, OpenAICallFunctionReturn]],
    Callable[P, OpenAICallResponse],
]:
    ...  # pragma: no cover


@overload
def openai_call(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[ResponseModelT],
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[P, OpenAICallFunctionReturn]],
    Callable[P, ResponseModelT],
]:
    ...  # pragma: no cover


@overload
def openai_call(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[P, OpenAICallFunctionReturn]],
    Callable[P, OpenAIStream],
]:
    ...  # pragma: no cover


@overload
def openai_call(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[ResponseModelT],
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[P, OpenAICallFunctionReturn]],
    Callable[P, Iterable[ResponseModelT]],
]:
    ...  # pragma: no cover


def openai_call(
    model: str,
    *,
    stream: bool = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[ResponseModelT] | None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[P, OpenAICallFunctionReturn]],
    Callable[
        P,
        OpenAICallResponse | OpenAIStream | ResponseModelT | Iterable[ResponseModelT],
    ],
]:
    '''A decorator for calling the OpenAI API with a typed function.

    This decorator is used to wrap a typed function that calls the OpenAI API. It parses
    the docstring of the wrapped function as the messages array and templates the input
    arguments for the function into each message's template.

    Example:

    ```python
    @openai_call(model="gpt-4o")
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    response = recommend_book("fantasy")
    ```

    Args:
        model: The OpenAI model to use in the API call.
        stream: Whether to stream the response from the API call.
        tools: The tools to use in the OpenAI API call.
        **call_params: The `OpenAICallParams` call parameters to use in the API call.

    Returns:
        The decorator for turning a typed function into an OpenAI API call.
    '''
    if response_model is not None:
        raise ValueError("`response_model` is not yet supported.")

    def call_decorator(
        fn: Callable[P, OpenAICallFunctionReturn],
    ) -> Callable[P, OpenAICallResponse]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> OpenAICallResponse:
            fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
            fn_return = fn(*args, **kwargs)
            prompt_template, messages, tool_types, call_kwargs = setup_call(
                fn, fn_args, fn_return, tools, call_params
            )
            client = OpenAI()
            start_time = datetime.datetime.now().timestamp() * 1000
            response = client.chat.completions.create(
                model=model, stream=False, messages=messages, **call_kwargs
            )
            return OpenAICallResponse(
                response=response,
                tool_types=tool_types,
                prompt_template=prompt_template,
                fn_args=fn_args,
                fn_return=fn_return,
                messages=messages,
                call_params=call_kwargs,
                user_message_param=messages[-1]
                if messages[-1]["role"] == "user"
                else None,
                start_time=start_time,
                end_time=datetime.datetime.now().timestamp() * 1000,
                cost=None,  # NEED THIS FIXED
            )

        return inner

    def stream_decorator(
        fn: Callable[P, OpenAICallFunctionReturn],
    ) -> Callable[P, OpenAIStream]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> OpenAIStream:
            fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
            fn_return = fn(*args, **kwargs)
            _, messages, tool_types, call_kwargs = setup_call(
                fn, fn_args, fn_return, tools, call_params
            )
            client = OpenAI()
            stream = client.chat.completions.create(
                model=model, stream=True, messages=messages, **call_kwargs
            )

            def generator():
                for chunk in stream:
                    yield OpenAICallResponseChunk(
                        chunk=chunk,
                        user_message_param=messages[-1]
                        if messages[-1]["role"] == "user"
                        else None,
                        tool_types=tool_types,
                        cost=None,  # NEED THIS FIXED
                    )

            return OpenAIStream(generator())

        return inner

    if stream:
        return stream_decorator
    return call_decorator


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[P, Awaitable[OpenAICallResponse]],
]:
    ...  # pragma: no cover


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[ResponseModelT],
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[P, Awaitable[ResponseModelT]],
]:
    ...  # pragma: no cover


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[P, Awaitable[OpenAIAsyncStream]],
]:
    ...  # pragma: no cover


@overload
def openai_call_async(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[ResponseModelT],
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[P, Awaitable[AsyncIterable[ResponseModelT]]],
]:
    ...  # pragma: no cover


def openai_call_async(
    model: str,
    *,
    stream: bool = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[ResponseModelT] | None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[
        P,
        Awaitable[OpenAICallResponse]
        | Awaitable[OpenAIAsyncStream]
        | Awaitable[ResponseModelT]
        | Awaitable[AsyncIterable[ResponseModelT]],
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
    if response_model is not None:
        raise ValueError("`response_model` is not yet supported.")

    def call_decorator(
        fn: Callable[P, Awaitable[OpenAICallFunctionReturn]],
    ) -> Callable[P, Awaitable[OpenAICallResponse]]:
        async def inner_async(*args: P.args, **kwargs: P.kwargs) -> OpenAICallResponse:
            fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
            fn_return = await fn(*args, **kwargs)
            prompt_template, messages, tool_types, call_kwargs = setup_call(
                fn, fn_args, fn_return, tools, call_params
            )
            client = AsyncOpenAI()
            start_time = datetime.datetime.now().timestamp() * 1000
            response = await client.chat.completions.create(
                model=model, stream=False, messages=messages, **call_kwargs
            )
            return OpenAICallResponse(
                response=response,
                tool_types=tool_types,
                prompt_template=prompt_template,
                fn_args=fn_args,
                fn_return=fn_return,
                messages=messages,
                call_params=call_kwargs,
                user_message_param=messages[-1]
                if messages[-1]["role"] == "user"
                else None,
                start_time=start_time,
                end_time=datetime.datetime.now().timestamp() * 1000,
                cost=None,  # NEED THIS FIXED
            )

        return inner_async

    def stream_decorator(
        fn: Callable[P, Awaitable[OpenAICallFunctionReturn]],
    ) -> Callable[P, Awaitable[OpenAIAsyncStream]]:
        async def inner_async(*args: P.args, **kwargs: P.kwargs) -> OpenAIAsyncStream:
            fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
            fn_return = await fn(*args, **kwargs)
            _, messages, tool_types, call_kwargs = setup_call(
                fn, fn_args, fn_return, tools, call_params
            )
            client = AsyncOpenAI()
            stream = await client.chat.completions.create(
                model=model, stream=True, messages=messages, **call_kwargs
            )

            async def generator():
                async for chunk in stream:
                    yield OpenAICallResponseChunk(
                        chunk=chunk,
                        user_message_param=messages[-1]
                        if messages[-1]["role"] == "user"
                        else None,
                        tool_types=tool_types,
                        cost=None,  # NEED THIS FIXED
                    )

            return OpenAIAsyncStream(generator())

        return inner_async

    if stream:
        return stream_decorator
    return call_decorator
