"""This module contains the setup_call function for Azure tools."""

import inspect
import os
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
from azure.core.credentials import AzureKeyCredential

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import AsyncCreateFn, CreateFn, get_async_create_fn, get_create_fn
from .._call_kwargs import AzureCallKwargs
from ..call_params import AzureCallParams
from ..dynamic_config import AsyncAzureDynamicConfig, AzureDynamicConfig
from ..tool import AzureTool, GenerateAzureStrictToolJsonSchema
from ._convert_message_params import convert_message_params
from ._get_credential import get_credential


@overload
def setup_call(
    *,
    model: str,
    client: AsyncChatCompletionsClient | None,
    fn: Callable[..., Awaitable[AsyncAzureDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AsyncAzureDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: AzureCallParams,
    extract: bool,
) -> tuple[
    AsyncCreateFn[ChatCompletions, StreamingChatCompletionsUpdate],
    str | None,
    list[ChatRequestMessage],
    list[type[AzureTool]] | None,
    AzureCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: ChatCompletionsClient | None,
    fn: Callable[..., AzureDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: AzureDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: AzureCallParams,
    extract: bool,
) -> tuple[
    CreateFn[ChatCompletions, StreamingChatCompletionsUpdate],
    str | None,
    list[ChatRequestMessage],
    list[type[AzureTool]] | None,
    AzureCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: ChatCompletionsClient | AsyncChatCompletionsClient | None,
    fn: Callable[..., AzureDynamicConfig]
    | Callable[..., Awaitable[AzureDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AzureDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: AzureCallParams,
    extract: bool,
) -> tuple[
    CreateFn[ChatCompletions, StreamingChatCompletionsUpdate]
    | AsyncCreateFn[ChatCompletions, StreamingChatCompletionsUpdate],
    str | None,
    list[ChatRequestMessage],
    list[type[AzureTool]] | None,
    AzureCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, AzureTool, call_params
    )
    call_kwargs = cast(AzureCallKwargs, base_call_kwargs)
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
                        schema_generator=GenerateAzureStrictToolJsonSchema
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
        endpoint = os.environ["AZURE_INFERENCE_ENDPOINT"]
        credential = cast(AzureKeyCredential, get_credential())

        client = (
            AsyncChatCompletionsClient(endpoint=endpoint, credential=credential)
            if inspect.iscoroutinefunction(fn)
            else ChatCompletionsClient(endpoint=endpoint, credential=credential)
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
