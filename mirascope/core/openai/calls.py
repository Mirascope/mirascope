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

from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI
from pydantic import BaseModel

from ..base import BaseTool, _utils
from ._utils import extract_tool_return, setup_call, setup_extract, setup_extract_tool
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .cost import openai_api_calculate_cost
from .function_return import OpenAICallFunctionReturn
from .streams import OpenAIAsyncStream, OpenAIStream
from .structured_streams import OpenAIAsyncStructuredStream, OpenAIStructuredStream
from .tools import OpenAITool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


@overload
def openai_call(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, OpenAICallFunctionReturn]],
    Callable[_P, OpenAICallResponse],
]:
    ...  # pragma: no cover


@overload
def openai_call(
    model: str,
    *,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, OpenAICallFunctionReturn]],
    Callable[_P, _ResponseModelT],
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
    [Callable[_P, OpenAICallFunctionReturn]],
    Callable[_P, OpenAIStream],
]:
    ...  # pragma: no cover


@overload
def openai_call(
    model: str,
    *,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, OpenAICallFunctionReturn]],
    Callable[_P, Iterable[_ResponseModelT]],
]:
    ...  # pragma: no cover


def openai_call(
    model: str,
    *,
    stream: bool = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, OpenAICallFunctionReturn]],
    Callable[
        _P,
        OpenAICallResponse | OpenAIStream | _ResponseModelT | Iterable[_ResponseModelT],
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

    def call_decorator(
        fn: Callable[_P, OpenAICallFunctionReturn],
    ) -> Callable[_P, OpenAICallResponse]:
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> OpenAICallResponse:
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
                cost=openai_api_calculate_cost(response.usage, response.model),
            )

        return inner

    def stream_decorator(
        fn: Callable[_P, OpenAICallFunctionReturn],
    ) -> Callable[_P, OpenAIStream]:
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> OpenAIStream:
            fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
            fn_return = fn(*args, **kwargs)
            _, messages, tool_types, call_kwargs = setup_call(
                fn, fn_args, fn_return, tools, call_params
            )
            client = OpenAI()

            if not isinstance(client, AzureOpenAI):
                call_kwargs["stream_options"] = {"include_usage": True}

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
                        cost=openai_api_calculate_cost(chunk.usage, chunk.model),
                    )

            return OpenAIStream(generator())

        return inner

    def extract_decorator(
        fn: Callable[_P, OpenAICallFunctionReturn],
    ) -> Callable[_P, _ResponseModelT]:
        assert response_model is not None
        tool = setup_extract_tool(response_model)

        def inner(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
            assert response_model is not None
            fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
            fn_return = fn(*args, **kwargs)
            json_mode, messages, call_kwargs = setup_extract(
                fn, fn_args, fn_return, tool, call_params
            )
            client = OpenAI()
            response = client.chat.completions.create(
                model=model, stream=False, messages=messages, **call_kwargs
            )

            if json_mode and (content := response.choices[0].message.content):
                json_output = content
            elif tool_calls := response.choices[0].message.tool_calls:
                json_output = tool_calls[0].function.arguments
            else:
                raise ValueError("No tool call or JSON object found in response.")

            output = extract_tool_return(response_model, json_output, False)
            if isinstance(response_model, BaseModel):
                output._response = response  # type: ignore
            return output

        return inner

    def extract_stream_decorator(
        fn: Callable[_P, OpenAICallFunctionReturn],
    ) -> Callable[_P, Iterable[_ResponseModelT]]:
        assert response_model is not None
        tool = setup_extract_tool(response_model)

        def inner(*args: _P.args, **kwargs: _P.kwargs) -> Iterable[_ResponseModelT]:
            assert response_model is not None
            fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
            fn_return = fn(*args, **kwargs)
            json_mode, messages, call_kwargs = setup_extract(
                fn, fn_args, fn_return, tool, call_params
            )
            client = OpenAI()
            return OpenAIStructuredStream(
                stream=(
                    chunk
                    for chunk in client.chat.completions.create(
                        model=model, stream=True, messages=messages, **call_kwargs
                    )
                ),
                response_model=response_model,
                json_mode=json_mode,
            )

        return inner

    if response_model:
        return extract_stream_decorator if stream else extract_decorator
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
    response_model: type[_ResponseModelT],
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
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
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
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]],
]:
    ...  # pragma: no cover


def openai_call_async(
    model: str,
    *,
    stream: bool = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    **call_params: Unpack[OpenAICallParams],
) -> Callable[
    [Callable[_P, Awaitable[OpenAICallFunctionReturn]]],
    Callable[
        _P,
        Awaitable[OpenAICallResponse]
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

    def call_decorator(
        fn: Callable[_P, Awaitable[OpenAICallFunctionReturn]],
    ) -> Callable[_P, Awaitable[OpenAICallResponse]]:
        async def inner_async(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> OpenAICallResponse:
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
                cost=openai_api_calculate_cost(response.usage, response.model),
            )

        return inner_async

    def stream_decorator(
        fn: Callable[_P, Awaitable[OpenAICallFunctionReturn]],
    ) -> Callable[_P, Awaitable[OpenAIAsyncStream]]:
        async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> OpenAIAsyncStream:
            fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
            fn_return = await fn(*args, **kwargs)
            _, messages, tool_types, call_kwargs = setup_call(
                fn, fn_args, fn_return, tools, call_params
            )
            client = AsyncOpenAI()

            if not isinstance(client, AsyncAzureOpenAI):
                call_kwargs["stream_options"] = {"include_usage": True}

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
                        cost=openai_api_calculate_cost(chunk.usage, chunk.model),
                    )

            return OpenAIAsyncStream(generator())

        return inner_async

    def extract_decorator(
        fn: Callable[_P, Awaitable[OpenAICallFunctionReturn]],
    ) -> Callable[_P, Awaitable[_ResponseModelT]]:
        nonlocal response_model
        assert response_model is not None
        tool = setup_extract_tool(response_model)

        async def inner(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
            assert response_model is not None
            fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
            fn_return = await fn(*args, **kwargs)
            json_mode, messages, call_kwargs = setup_extract(
                fn, fn_args, fn_return, tool, call_params
            )
            client = AsyncOpenAI()
            response = await client.chat.completions.create(
                model=model, stream=False, messages=messages, **call_kwargs
            )

            if json_mode and (content := response.choices[0].message.content):
                json_output = content
            elif tool_calls := response.choices[0].message.tool_calls:
                json_output = tool_calls[0].function.arguments
            else:
                raise ValueError("No tool call or JSON object found in response.")

            output = extract_tool_return(response_model, json_output, False)
            if isinstance(response_model, BaseModel):
                output._response = response  # type: ignore
            return output

        return inner

    def extract_stream_decorator(
        fn: Callable[_P, Awaitable[OpenAICallFunctionReturn]],
    ) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]:
        assert response_model is not None
        tool = setup_extract_tool(response_model)

        async def inner(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> AsyncIterable[_ResponseModelT]:
            assert response_model is not None
            fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
            fn_return = await fn(*args, **kwargs)
            json_mode, messages, call_kwargs = setup_extract(
                fn, fn_args, fn_return, tool, call_params
            )
            client = AsyncOpenAI()
            return OpenAIAsyncStructuredStream(
                stream=(
                    chunk
                    async for chunk in await client.chat.completions.create(
                        model=model, stream=True, messages=messages, **call_kwargs
                    )
                ),
                response_model=response_model,
                json_mode=json_mode,
            )

        return inner

    if response_model:
        return extract_stream_decorator if stream else extract_decorator
    if stream:
        return stream_decorator
    return call_decorator
