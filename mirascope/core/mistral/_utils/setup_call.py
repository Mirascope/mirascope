"""This module contains the setup_call function for Mistral tools."""

import inspect
from typing import Any, Awaitable, Callable

from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.models.chat_completion import (
    ChatCompletionResponse,
    ResponseFormat,
    ResponseFormats,
    ToolChoice,
)

from ...base import BaseMessageParam, BaseTool, _utils
from ..call_params import MistralCallParams
from ..dynamic_config import MistralDynamicConfig
from ..tool import MistralTool


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
    list[dict[str, BaseMessageParam]],
    list[type[MistralTool]] | None,
    dict[str, Any],
]:
    prompt_template, messages, tool_types, call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, MistralTool, call_params
    )
    if client is None:
        client = (
            MistralAsyncClient() if inspect.iscoroutinefunction(fn) else MistralClient()
        )
    call_kwargs |= {"model": model, "messages": messages}
    if json_mode:
        call_kwargs["response_format"] = ResponseFormat(
            type=ResponseFormats("json_object")
        )
        messages[-1]["content"] += _utils.json_mode_content(
            tool_types[0] if tool_types else None
        )
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        call_kwargs["tool_choice"] = ToolChoice.any

    def create_or_stream(stream: bool, **kwargs: Any):
        if stream:
            return client.chat_stream(**kwargs)
        return client.chat(**kwargs)

    return create_or_stream, prompt_template, messages, tool_types, call_kwargs  # type: ignore
