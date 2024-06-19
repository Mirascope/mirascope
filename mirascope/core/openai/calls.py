"""The `openai_call` decorator for easy OpenAI API typed functions."""

import datetime
import inspect
from typing import (
    Awaitable,
    Callable,
    ParamSpec,
    Unpack,
    overload,
)

from openai import AsyncOpenAI, OpenAI

from ..base.types import BaseTool
from .types import (
    OpenAICallFunctionReturn,
    OpenAICallParams,
    OpenAICallResponse,
)
from .utils import setup_call

P = ParamSpec("P")


def openai_call(
    tools: list[type[BaseTool] | Callable] | None = None,
    **call_params: Unpack[OpenAICallParams],
):
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
        tools: The tools to use in the OpenAI API call.
        **call_params: The `OpenAICallParams` call parameters to use in the API call.

    Returns:
        The decorator for turning a typed function into an OpenAI API call.
    '''

    @overload
    def call_decorator(
        fn: Callable[P, OpenAICallFunctionReturn],
    ) -> Callable[P, OpenAICallResponse]:
        ...  # pragma: no cover

    @overload
    def call_decorator(
        fn: Callable[P, Awaitable[OpenAICallFunctionReturn]],
    ) -> Callable[P, Awaitable[OpenAICallResponse]]:
        ...  # pragma: no cover

    def call_decorator(
        fn: Callable[P, OpenAICallFunctionReturn | Awaitable[OpenAICallFunctionReturn]],
    ) -> Callable[P, OpenAICallResponse | Awaitable[OpenAICallResponse]]:
        if inspect.iscoroutinefunction(fn):

            async def inner_async(
                *args: P.args, **kwargs: P.kwargs
            ) -> OpenAICallResponse:
                fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
                fn_return = await fn(*args, **kwargs)
                prompt_template, messages, tool_types, call_kwargs = setup_call(
                    fn, fn_args, fn_return, tools, call_params
                )
                client = AsyncOpenAI()
                start_time = datetime.datetime.now().timestamp() * 1000
                response = await client.chat.completions.create(
                    messages=messages, **call_kwargs
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
        else:

            def inner(*args: P.args, **kwargs: P.kwargs) -> OpenAICallResponse:
                fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
                fn_return = fn(*args, **kwargs)
                assert not inspect.isawaitable(fn_return)
                prompt_template, messages, tool_types, call_kwargs = setup_call(
                    fn, fn_args, fn_return, tools, call_params
                )
                client = OpenAI()
                start_time = datetime.datetime.now().timestamp() * 1000
                response = client.chat.completions.create(
                    messages=messages, **call_kwargs
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

    return call_decorator
