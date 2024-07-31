"""This module contains the setup_call function for OpenAI tools."""

import inspect
from typing import Any, Awaitable, Callable

from litellm import acompletion, completion
from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from ...base import BaseTool
from ...openai import OpenAICallParams, OpenAIDynamicConfig, OpenAITool
from ...openai._utils import setup_call as setup_call_openai


def setup_call(
    *,
    model: str,
    client: OpenAI | AsyncOpenAI | AzureOpenAI | AsyncAzureOpenAI | None,
    fn: Callable[..., OpenAIDynamicConfig | Awaitable[OpenAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: OpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams,
    extract: bool,
) -> tuple[
    Callable[..., ChatCompletion] | Callable[..., Awaitable[ChatCompletion]],
    str,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    dict[str, Any],
]:
    _, prompt_template, messages, tool_types, call_kwargs = setup_call_openai(
        model=model,
        client=client,
        fn=fn,
        fn_args=fn_args,
        dynamic_config=dynamic_config,
        tools=tools,
        json_mode=json_mode,
        call_params=call_params,
        extract=extract,
    )
    create = acompletion if inspect.iscoroutinefunction(fn) else completion
    return create, prompt_template, messages, tool_types, call_kwargs  # type: ignore
