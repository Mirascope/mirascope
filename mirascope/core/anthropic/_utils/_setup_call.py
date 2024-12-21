"""This module contains the setup_call function for the Anthropic API."""

import inspect
from collections.abc import Awaitable, Callable
from typing import Any, cast, overload

from anthropic import (
    Anthropic,
    AnthropicBedrock,
    AnthropicVertex,
    AsyncAnthropic,
    AsyncAnthropicBedrock,
    AsyncAnthropicVertex,
)
from anthropic.types import Message, MessageParam, MessageStreamEvent
from pydantic import BaseModel

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import AsyncCreateFn, CreateFn
from ...base.stream_config import StreamConfig
from .._call_kwargs import AnthropicCallKwargs
from ..call_params import AnthropicCallParams
from ..dynamic_config import AnthropicDynamicConfig, AsyncAnthropicDynamicConfig
from ..tool import AnthropicTool
from ._convert_common_call_params import convert_common_call_params
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: AsyncAnthropic | AsyncAnthropicBedrock | AsyncAnthropicVertex | None,
    fn: Callable[..., Awaitable[AsyncAnthropicDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AsyncAnthropicDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: AnthropicCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    AsyncCreateFn[Message, MessageStreamEvent],
    str | None,
    list[MessageParam],
    list[type[AnthropicTool]] | None,
    AnthropicCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: Anthropic | AnthropicBedrock | AnthropicVertex | None,
    fn: Callable[..., AnthropicDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: AnthropicDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: AnthropicCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    CreateFn[Message, MessageStreamEvent],
    str | None,
    list[MessageParam],
    list[type[AnthropicTool]] | None,
    AnthropicCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: Anthropic
    | AsyncAnthropic
    | AnthropicBedrock
    | AsyncAnthropicBedrock
    | AnthropicVertex
    | AsyncAnthropicVertex
    | None,
    fn: Callable[..., AnthropicDynamicConfig | Awaitable[AsyncAnthropicDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AsyncAnthropicDynamicConfig | AnthropicDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: AnthropicCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    Callable[..., Message | Awaitable[Message]],
    str | None,
    list[MessageParam],
    list[type[AnthropicTool]] | None,
    AnthropicCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn,
        fn_args,
        dynamic_config,
        tools,
        AnthropicTool,
        call_params,
        convert_common_call_params,
    )
    call_kwargs = cast(AnthropicCallKwargs, base_call_kwargs)
    messages = cast(list[BaseMessageParam | MessageParam], messages)
    messages = convert_message_params(messages)

    if messages[0]["role"] == "system":
        call_kwargs["system"] = messages.pop(0)["content"]  # pyright: ignore [reportGeneralTypeIssues]

    if json_mode:
        json_mode_content = _utils.json_mode_content(response_model)
        if isinstance(messages[-1]["content"], str):
            messages[-1]["content"] += json_mode_content
        else:
            messages[-1]["content"] = list(messages[-1]["content"]) + [
                {"type": "text", "text": json_mode_content}
            ]
    elif response_model:
        assert tool_types, "At least one tool must be provided for extraction."
        call_kwargs["tool_choice"] = {"type": "tool", "name": tool_types[0]._name()}
    call_kwargs |= {
        "model": model,
        "messages": messages,
        "max_tokens": call_kwargs["max_tokens"],
    }

    if client is None:
        client = AsyncAnthropic() if inspect.iscoroutinefunction(fn) else Anthropic()
    create = client.messages.create
    return create, prompt_template, messages, tool_types, call_kwargs
