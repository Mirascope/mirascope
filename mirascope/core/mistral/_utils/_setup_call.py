"""This module contains the setup_call function for Mistral tools."""

import inspect
from collections.abc import (
    Awaitable,
    Callable,
)
from typing import Any, cast, overload

from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.models.chat_completion import (
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    ChatMessage,
    ResponseFormat,
    ResponseFormats,
    ToolChoice,
)

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import AsyncCreateFn, CreateFn, get_async_create_fn, get_create_fn
from .._call_kwargs import MistralCallKwargs
from ..call_params import MistralCallParams
from ..dynamic_config import AsyncMistralDynamicConfig, MistralDynamicConfig
from ..tool import MistralTool
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: MistralAsyncClient | None,
    fn: Callable[..., Awaitable[AsyncMistralDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AsyncMistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams,
    extract: bool,
) -> tuple[
    AsyncCreateFn[ChatCompletionResponse, ChatCompletionStreamResponse],
    str | None,
    list[ChatMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: MistralClient | None,
    fn: Callable[..., MistralDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams,
    extract: bool,
) -> tuple[
    CreateFn[ChatCompletionResponse, ChatCompletionStreamResponse],
    str | None,
    list[ChatMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: MistralClient | MistralAsyncClient | None,
    fn: Callable[..., MistralDynamicConfig | Awaitable[AsyncMistralDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig | AsyncMistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams,
    extract: bool,
) -> tuple[
    CreateFn[ChatCompletionResponse, ChatCompletionStreamResponse]
    | AsyncCreateFn[ChatCompletionResponse, ChatCompletionStreamResponse],
    str | None,
    list[ChatMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, MistralTool, call_params
    )
    call_kwargs = cast(MistralCallKwargs, base_call_kwargs)
    messages = cast(list[BaseMessageParam | ChatMessage], messages)
    messages = convert_message_params(messages)
    if json_mode:
        call_kwargs["response_format"] = ResponseFormat(
            type=ResponseFormats("json_object")
        )
        json_mode_content = _utils.json_mode_content(
            tool_types[0] if tool_types else None
        )
        if messages[-1].role == "user":
            messages[-1].content += json_mode_content
        else:
            messages.append(ChatMessage(role="user", content=json_mode_content.strip()))
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        call_kwargs["tool_choice"] = cast(ToolChoice, ToolChoice.any)
    call_kwargs |= {"model": model, "messages": messages}

    if client is None:
        client = (
            MistralAsyncClient() if inspect.iscoroutinefunction(fn) else MistralClient()
        )
    if isinstance(client, MistralAsyncClient):
        create_or_stream = get_async_create_fn(client.chat, client.chat_stream)
    else:
        create_or_stream = get_create_fn(client.chat, client.chat_stream)
    return create_or_stream, prompt_template, messages, tool_types, call_kwargs
