"""This module contains the setup_call function for OpenAI tools."""

from collections.abc import Awaitable, Callable
from typing import Any, TypeAlias, cast, overload

from litellm import acompletion, completion
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
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

# Note: MyPy doesn't like `client: ...` so we use these aliases instead.
_AsyncLiteLLMClient: TypeAlias = Any
_SyncLiteLLMClient: TypeAlias = Any


@overload
def setup_call(
    *,
    model: str,
    client: _AsyncLiteLLMClient | None,
    fn: Callable[..., Awaitable[AsyncOpenAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AsyncOpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    AsyncCreateFn[ChatCompletion, ChatCompletion],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: _SyncLiteLLMClient | None,
    fn: Callable[..., OpenAIDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: OpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    CreateFn[ChatCompletion, ChatCompletion],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: None,
    fn: Callable[..., OpenAIDynamicConfig | Awaitable[AsyncOpenAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: OpenAIDynamicConfig | AsyncOpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    CreateFn[ChatCompletion, ChatCompletion]
    | AsyncCreateFn[ChatCompletion, ChatCompletion],
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
        response_model=response_model,
        stream=stream,
    )
    create = cast(
        Callable[..., ChatCompletion] | Callable[..., Awaitable[ChatCompletion]],
        acompletion if fn_is_async(fn) else completion,
    )
    return create, prompt_template, messages, tool_types, call_kwargs
