"""This module contains the setup_call function for Groq tools."""

import inspect
from collections.abc import Awaitable, Callable
from typing import Any, cast, overload

from groq import AsyncGroq, Groq
from groq.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
)

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import AsyncCreateFn, CreateFn, get_async_create_fn, get_create_fn
from ...base.call_params import CommonCallParams
from ...base.stream_config import StreamConfig
from .._call_kwargs import GroqCallKwargs
from ..call_params import GroqCallParams
from ..dynamic_config import AsyncGroqDynamicConfig, GroqDynamicConfig
from ..tool import GroqTool
from ._convert_common_call_params import convert_common_call_params
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: AsyncGroq | None,
    fn: Callable[..., Awaitable[AsyncGroqDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AsyncGroqDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: GroqCallParams | CommonCallParams,
    extract: bool,
    stream: bool | StreamConfig,
) -> tuple[
    AsyncCreateFn[ChatCompletion, ChatCompletionChunk],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[GroqTool]] | None,
    GroqCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: Groq | None,
    fn: Callable[..., GroqDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: GroqDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: GroqCallParams | CommonCallParams,
    extract: bool,
    stream: bool | StreamConfig,
) -> tuple[
    CreateFn[ChatCompletion, ChatCompletionChunk],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[GroqTool]] | None,
    GroqCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: Groq | AsyncGroq | None,
    fn: Callable[..., GroqDynamicConfig | Awaitable[AsyncGroqDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: GroqDynamicConfig | AsyncGroqDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: GroqCallParams | CommonCallParams,
    extract: bool,
    stream: bool | StreamConfig,
) -> tuple[
    CreateFn[ChatCompletion, ChatCompletionChunk]
    | AsyncCreateFn[ChatCompletion, ChatCompletionChunk],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[GroqTool]] | None,
    GroqCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn,
        fn_args,
        dynamic_config,
        tools,
        GroqTool,
        call_params,
        convert_common_call_params,
    )
    call_kwargs = cast(GroqCallKwargs, base_call_kwargs)
    messages = cast(list[BaseMessageParam | ChatCompletionMessageParam], messages)
    messages = convert_message_params(messages)
    if json_mode:
        call_kwargs["response_format"] = {"type": "json_object"}
        json_mode_content = _utils.json_mode_content(
            tool_types[0] if tool_types else None
        )
        if messages[-1]["role"] == "user":
            if isinstance(messages[-1]["content"], str):
                messages[-1]["content"] += json_mode_content
            else:
                messages[-1]["content"] = list(messages[-1]["content"]) + [
                    {"type": "text", "text": json_mode_content.strip()}
                ]
        else:
            messages.append({"role": "user", "content": json_mode_content.strip()})
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        call_kwargs["tool_choice"] = {
            "type": "function",
            "function": {"name": tool_types[0]._name()},
        }
    call_kwargs |= {"model": model, "messages": messages}

    if client is None:
        client = AsyncGroq() if inspect.iscoroutinefunction(fn) else Groq()

    create = (
        get_async_create_fn(client.chat.completions.create)
        if isinstance(client, AsyncGroq)
        else get_create_fn(client.chat.completions.create)
    )

    return create, prompt_template, messages, tool_types, call_kwargs
