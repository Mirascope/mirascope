"""This module contains the setup_call function for OpenAI tools."""

from collections.abc import Awaitable, Callable
from typing import Any, cast, overload

from litellm import acompletion, completion
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from ...base import BaseTool
from ...base._utils import fn_is_async
from ...openai import OpenAICallParams, OpenAIDynamicConfig, OpenAITool
from ...openai._utils import setup_call as setup_call_openai
from ...openai.call_kwargs import OpenAICallKwargs


@overload
def setup_call(
    *,
    model: str,
    client: None,
    fn: Callable[..., Awaitable[OpenAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: OpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams,
    extract: bool,
) -> tuple[
    Callable[..., Awaitable[ChatCompletion]],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: None,
    fn: Callable[..., OpenAIDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: OpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams,
    extract: bool,
) -> tuple[
    Callable[..., ChatCompletion],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: None,
    fn: Callable[..., OpenAIDynamicConfig | Awaitable[OpenAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: OpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams,
    extract: bool,
) -> tuple[
    Callable[..., ChatCompletion] | Callable[..., Awaitable[ChatCompletion]],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallKwargs,
]:
    _, prompt_template, messages, tool_types, call_kwargs = setup_call_openai(
        model=model,  # pyright: ignore [reportCallIssue]
        client=OpenAI(api_key="NOT_USED"),
        fn=fn,  # pyright: ignore [reportArgumentType]
        fn_args=fn_args,  # pyright: ignore [reportArgumentType]
        dynamic_config=dynamic_config,
        tools=tools,
        json_mode=json_mode,
        call_params=call_params,
        extract=extract,
    )
    create = cast(
        Callable[..., ChatCompletion] | Callable[..., Awaitable[ChatCompletion]],
        acompletion if fn_is_async(fn) else completion,
    )
    return create, prompt_template, messages, tool_types, call_kwargs
