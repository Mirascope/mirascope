"""This module contains the setup_call function for AzureAI tools."""

import inspect
import warnings
from collections.abc import AsyncIterable, Awaitable, Callable, Iterable
from typing import Any, cast, overload

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
from azure.ai.inference.models import (
    ChatCompletions,
    ChatCompletionsResponseFormatJSON,
    ChatRequestMessage,
    StreamingChatCompletionsUpdate,
    UserMessage,
)

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import AsyncCreateFn, CreateFn, get_async_create_fn, get_create_fn
from ..call_kwargs import AzureAICallKwargs
from ..call_params import AzureAICallParams
from ..dynamic_config import AzureAIDynamicConfig
from ..tool import AzureAITool, GenerateAzureAIStrictToolJsonSchema
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: ChatCompletionsClient | None,
    fn: Callable[..., Awaitable[AzureAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AzureAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: AzureAICallParams,
    extract: bool,
) -> tuple[
    AsyncCreateFn[ChatCompletions, StreamingChatCompletionsUpdate],
    str | None,
    list[ChatRequestMessage],
    list[type[AzureAITool]] | None,
    AzureAICallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: ChatCompletionsClient | None,
    fn: Callable[..., AzureAIDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: AzureAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: AzureAICallParams,
    extract: bool,
) -> tuple[
    CreateFn[ChatCompletions, StreamingChatCompletionsUpdate],
    str | None,
    list[ChatRequestMessage],
    list[type[AzureAITool]] | None,
    AzureAICallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: ChatCompletionsClient | AsyncChatCompletionsClient | None,
    fn: Callable[..., AzureAIDynamicConfig]
    | Callable[..., Awaitable[AzureAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AzureAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: AzureAICallParams,
    extract: bool,
) -> tuple[
    CreateFn[ChatCompletions, StreamingChatCompletionsUpdate]
    | AsyncCreateFn[ChatCompletions, StreamingChatCompletionsUpdate],
    str | None,
    list[ChatRequestMessage],
    list[type[AzureAITool]] | None,
    AzureAICallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, AzureAITool, call_params
    )
    call_kwargs = cast(AzureAICallKwargs, base_call_kwargs)
    messages = cast(list[BaseMessageParam | ChatRequestMessage], messages)
    messages = convert_message_params(messages)
    if json_mode:
        if tool_types and tool_types[0].model_config.get("strict", False):
            call_kwargs["response_format"] = ChatCompletionsResponseFormatJSON(
                {
                    "name": tool_types[0]._name(),
                    "description": tool_types[0]._description(),
                    "strict": True,
                    "schema": tool_types[0].model_json_schema(
                        schema_generator=GenerateAzureAIStrictToolJsonSchema
                    ),
                }
            )
        else:
            call_kwargs["response_format"] = ChatCompletionsResponseFormatJSON()
            json_mode_content = _utils.json_mode_content(
                tool_types[0] if tool_types else None
            ).strip()
            messages.append(UserMessage(content=json_mode_content))
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        if tool_types and tool_types[0].model_config.get("strict", False):
            warnings.warn(
                "You must set `json_mode=True` to use `strict=True` response models. "
                "Ignoring `strict` and using tools for extraction.",
                UserWarning,
            )
        call_kwargs["tool_choice"] = "required"
    call_kwargs |= {"model": model, "messages": messages}

    if client is None:
        # TODO: How to set up endpoint and credential?
        client = (
            ChatCompletionsClient(endpoint="", credential="")  # pyright: ignore [reportArgumentType]
            if inspect.iscoroutinefunction(fn)
            else AsyncChatCompletionsClient(endpoint="", credential="")  # pyright: ignore [reportArgumentType]
        )
    create = (
        get_async_create_fn(
            cast(
                AsyncCreateFn[
                    ChatCompletions, AsyncIterable[StreamingChatCompletionsUpdate]
                ],
                client.complete,
            )
        )
        if isinstance(client, AsyncChatCompletionsClient)
        else get_create_fn(
            cast(
                CreateFn[ChatCompletions, Iterable[StreamingChatCompletionsUpdate]],
                client.complete,
            )
        )
    )
    return create, prompt_template, messages, tool_types, call_kwargs
