"""The `openai_call` decorator for easy OpenAI API typed functions."""

import datetime
import inspect
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar, Unpack, overload

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletionMessageParam

from .._internal import utils
from ..base.types import BaseTool
from .types import (
    OpenAICallFunctionReturn,
    OpenAICallParams,
    OpenAICallResponse,
    OpenAITool,
)

P = ParamSpec("P")
R = TypeVar("R")


def _setup(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: OpenAICallFunctionReturn,
    tools: list[BaseTool] | None,
    call_params: OpenAICallParams,
) -> tuple[
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallParams,
]:
    prompt_template, messages, computed_fields = None, None, None
    if fn_return is not None:
        computed_fields = fn_return.get("computed_fields", None)
        tools = fn_return.get("tools", tools)
        messages = fn_return.get("messages", None)
        dynamic_call_params = fn_return.get("call_params", None)
        if dynamic_call_params:
            call_params |= dynamic_call_params

    if not messages:
        prompt_template = inspect.getdoc(fn)
        assert prompt_template is not None, "The function must have a docstring."
        if computed_fields:
            fn_args |= computed_fields
        messages = utils.parse_prompt_messages(
            roles=["system", "user", "assistant"],
            template=prompt_template,
            attrs=fn_args,
        )

    tool_types = None
    if tools:
        tool_types = [
            utils.convert_base_model_to_base_tool(tool, OpenAITool)  # type: ignore
            if inspect.isclass(tool)
            else utils.convert_function_to_base_tool(tool, OpenAITool)  # type: ignore
            for tool in tools
        ]
        call_params["tools"] = [tool_type.tool_schema() for tool_type in tool_types]  # type: ignore

    return prompt_template, messages, tool_types, call_params


def openai_call(
    tools: list[BaseTool] | None = None, **call_params: Unpack[OpenAICallParams]
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
    def decorator(
        fn: Callable[P, OpenAICallFunctionReturn],
    ) -> Callable[P, OpenAICallResponse]:
        ...  # pragma: no cover

    @overload
    def decorator(
        fn: Callable[P, Awaitable[OpenAICallFunctionReturn]],
    ) -> Callable[P, Awaitable[OpenAICallResponse]]:
        ...  # pragma: no cover

    def decorator(
        fn: Callable[P, OpenAICallFunctionReturn | Awaitable[OpenAICallFunctionReturn]],
    ) -> Callable[P, OpenAICallResponse | Awaitable[OpenAICallResponse]]:
        if inspect.iscoroutinefunction(fn):

            async def inner_async(
                *args: P.args, **kwargs: P.kwargs
            ) -> OpenAICallResponse:
                fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
                fn_return = await fn(*args, **kwargs)
                prompt_template, messages, tool_types, call_kwargs = _setup(
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
                prompt_template, messages, tool_types, call_kwargs = _setup(
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

    return decorator
