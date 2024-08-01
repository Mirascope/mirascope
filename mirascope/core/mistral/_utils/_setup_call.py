"""This module contains the setup_call function for Mistral tools."""

import inspect
from typing import Any, Awaitable, Callable, cast

from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.models.chat_completion import (
    ChatCompletionResponse,
    ChatMessage,
    ResponseFormat,
    ResponseFormats,
    ToolChoice,
)

from ...base import BaseMessageParam, BaseTool, _utils
from ..call_params import MistralCallParams
from ..dynamic_config import MistralDynamicConfig
from ..tool import MistralTool
from ._convert_message_params import convert_message_params


def setup_call(
    *,
    model: str,
    client: MistralClient | MistralAsyncClient | None,
    fn: Callable[..., MistralDynamicConfig | Awaitable[MistralDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams,
    extract: bool,
) -> tuple[
    Callable[..., ChatCompletionResponse]
    | Callable[..., Awaitable[ChatCompletionResponse]],
    str,
    list[ChatMessage],
    list[type[MistralTool]] | None,
    dict[str, Any],
]:
    prompt_template, messages, tool_types, call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, MistralTool, call_params
    )
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
        call_kwargs["tool_choice"] = ToolChoice.any
    call_kwargs |= {"model": model, "messages": messages}

    if client is None:
        client = (
            MistralAsyncClient() if inspect.iscoroutinefunction(fn) else MistralClient()
        )

    def create_or_stream(stream: bool, **kwargs: Any):
        if stream:
            return client.chat_stream(**kwargs)
        return client.chat(**kwargs)

    return create_or_stream, prompt_template, messages, tool_types, call_kwargs  # type: ignore
