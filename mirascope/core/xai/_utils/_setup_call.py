"""This module contains the setup_call function for OpenAI tools."""

import os
from collections.abc import Awaitable, Callable
from typing import Any, overload

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
)
from pydantic import BaseModel

from ...base import BaseTool
from ...base._utils import AsyncCreateFn, CreateFn, fn_is_async
from ...base.call_params import CommonCallParams
from ...base.stream_config import StreamConfig
from ...openai import (
    AsyncOpenAIDynamicConfig,
    OpenAICallParams,
    OpenAIDynamicConfig,
    OpenAITool,
)
from ...openai._call_kwargs import OpenAICallKwargs
from ...openai._utils import setup_call as setup_call_openai


@overload
def setup_call(
    *,
    model: str,
    client: AsyncOpenAI | None,
    fn: Callable[..., Awaitable[AsyncOpenAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AsyncOpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    AsyncCreateFn[ChatCompletion, ChatCompletionChunk],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: OpenAI | None,
    fn: Callable[..., OpenAIDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: OpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    CreateFn[ChatCompletion, ChatCompletionChunk],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: OpenAI | AsyncOpenAI | None,
    fn: Callable[..., OpenAIDynamicConfig]
    | Callable[..., Awaitable[AsyncOpenAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: OpenAIDynamicConfig | AsyncOpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    CreateFn[ChatCompletion, ChatCompletionChunk]
    | AsyncCreateFn[ChatCompletion, ChatCompletionChunk],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallKwargs,
]:
    if not client:
        api_key = os.environ.get("XAI_API_KEY")
        client = (
            AsyncOpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
            if fn_is_async(fn)
            else OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        )
    create, prompt_template, messages, tool_types, call_kwargs = setup_call_openai(
        model=model,  # pyright: ignore [reportCallIssue]
        client=client,  # pyright: ignore [reportArgumentType]
        fn=fn,  # pyright: ignore [reportArgumentType]
        fn_args=fn_args,  # pyright: ignore [reportArgumentType]
        dynamic_config=dynamic_config,
        tools=tools,
        json_mode=json_mode,
        call_params=call_params,
        response_model=response_model,
        stream=stream,
    )
    return create, prompt_template, messages, tool_types, call_kwargs
