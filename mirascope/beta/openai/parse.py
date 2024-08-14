"""Beta implementation of the new OpenAI parse functionality."""

import inspect
from functools import wraps
from typing import Awaitable, Callable, Literal, ParamSpec, TypeVar, cast, overload

from pydantic import BaseModel

from mirascope.core.base import BaseMessageParam, _utils
from mirascope.core.openai import OpenAICallParams, OpenAIDynamicConfig, OpenAITool
from mirascope.core.openai._utils import convert_message_params
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletionMessageParam

_ResponseModelT = TypeVar("_ResponseModelT", bound=_utils.BaseType | BaseModel)
_P = ParamSpec("_P")


def parse(
    model: Literal["gpt-4o-2024-08-06"],
    response_model: type[_ResponseModelT],
    call_params: OpenAICallParams | None = None,
):
    """Beta implementation of the new OpenAI parse functionality."""

    @overload
    def decorator(
        fn: Callable[_P, OpenAIDynamicConfig],
    ) -> Callable[_P, _ResponseModelT]: ...

    @overload
    def decorator(
        fn: Callable[_P, Awaitable[OpenAIDynamicConfig]],
    ) -> Callable[_P, Awaitable[_ResponseModelT]]: ...

    def decorator(
        fn: Callable[_P, OpenAIDynamicConfig | Awaitable[OpenAIDynamicConfig]],
    ) -> Callable[_P, _ResponseModelT | Awaitable[_ResponseModelT]]:
        is_async = inspect.iscoroutinefunction(fn)

        @wraps(fn)
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
            assert _utils.SetupCall.fn_is_sync(fn)
            fn_args = _utils.get_fn_args(fn, args, kwargs)
            dynamic_config = fn(*args, **kwargs)
            _, messages, _, call_kwargs = _utils.setup_call(
                fn,
                fn_args,
                dynamic_config,
                None,
                OpenAITool,
                call_params or OpenAICallParams(),
            )
            messages = cast(
                list[BaseMessageParam | ChatCompletionMessageParam], messages
            )
            messages = convert_message_params(messages)
            messages.append({"role": "user", "content": _utils.json_mode_content(None)})
            client = OpenAI()
            call_kwargs.pop("response_format", None)
            completion = client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_model,
                **call_kwargs,
            )
            message = completion.choices[0].message
            if message.parsed:
                return message.parsed
            raise RuntimeError(f"{message.refusal}")

        @wraps(fn)
        async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
            assert _utils.SetupCall.fn_is_async(fn)
            fn_args = _utils.get_fn_args(fn, args, kwargs)
            dynamic_config = await fn(*args, **kwargs)
            _, messages, _, call_kwargs = _utils.setup_call(
                fn,
                fn_args,
                dynamic_config,
                None,
                OpenAITool,
                call_params or OpenAICallParams(),
            )
            messages = cast(
                list[BaseMessageParam | ChatCompletionMessageParam], messages
            )
            messages = convert_message_params(messages)
            messages.append({"role": "user", "content": _utils.json_mode_content(None)})
            client = AsyncOpenAI()
            call_kwargs.pop("response_format", None)
            completion = await client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_model,
                **call_kwargs,
            )
            message = completion.choices[0].message
            if message.parsed:
                return message.parsed
            raise RuntimeError(f"{message.refusal}")

        return inner_async if is_async else inner

    return decorator
