"""This module contains the setup_call function for the Anthropic API."""

import inspect
from typing import Any, Awaitable, Callable

from anthropic import Anthropic, AsyncAnthropic
from anthropic._base_client import BaseClient
from anthropic.types import Message, MessageParam

from ...base import BaseTool, _utils
from ..call_params import AnthropicCallParams
from ..dynamic_config import AnthropicDynamicConfig
from ..tool import AnthropicTool


def setup_call(
    *,
    model: str,
    client: BaseClient | None,
    fn: Callable[..., AnthropicDynamicConfig | Awaitable[AnthropicDynamicConfig]],
    fn_args: dict[str, any],
    dynamic_config: AnthropicDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: AnthropicCallParams,
    extract: bool,
) -> tuple[
    Callable[..., Message],
    str,
    list[dict[str, MessageParam]],
    list[type[AnthropicTool]],
    dict[str, Any],
]:
    prompt_template, messages, tool_types, call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, AnthropicTool, call_params
    )
    if messages[0]["role"] == "system":
        call_kwargs["system"] = messages.pop(0)["content"]
    if client is None:
        client = AsyncAnthropic() if inspect.iscoroutinefunction(fn) else Anthropic()
    create = client.messages.create
    call_kwargs |= {"model": model, "messages": messages}

    if json_mode:
        messages[-1]["content"] += _utils.json_mode_content(
            tool_types[0] if tools else None
        )
        call_kwargs.pop("tools", None)
    elif extract:
        call_kwargs["tool_choice"] = {"type": "tool", "name": tool_types[0]._name()}

    return create, prompt_template, messages, tool_types, call_kwargs
