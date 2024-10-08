"""This module contains the setup_call function for Bedrock tools."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from typing import Any, cast, overload

from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from mypy_boto3_bedrock_runtime.type_defs import (
    ConverseResponseTypeDef,
    ToolChoiceTypeDef,
    ToolConfigurationTypeDef,
)
from types_aiobotocore_bedrock_runtime import (
    BedrockRuntimeClient as AsyncBedrockRuntimeClient,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseResponseTypeDef as AsyncConverseResponseTypeDef,
)

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import AsyncCreateFn, CreateFn, get_async_create_fn, get_create_fn
from ..call_kwargs import BedrockCallKwargs
from ..call_params import BedrockCallParams
from ..dynamic_config import BedrockDynamicConfig
from ..tool import BedrockTool
from ._convert_message_params import convert_message_params
from ._extract_stream import _extract_async_stream_fn, _extract_sync_stream_fn
from ._get_client import _get_async_client, _get_sync_client
from ._types import (
    AsyncStreamOutputChunk,
    BedrockMessageParam,
    StreamOutputChunk,
)


@overload
def setup_call(
    *,
    model: str,
    client: BedrockRuntimeClient | AsyncBedrockRuntimeClient | None,
    fn: Callable[..., Awaitable[BedrockDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: BedrockDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: BedrockCallParams,
    extract: bool,
) -> tuple[
    AsyncCreateFn[AsyncConverseResponseTypeDef, AsyncStreamOutputChunk],
    str | None,
    list[BedrockMessageParam],
    list[type[BedrockTool]] | None,
    BedrockCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: BedrockRuntimeClient | AsyncBedrockRuntimeClient | None,
    fn: Callable[..., BedrockDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: BedrockDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: BedrockCallParams,
    extract: bool,
) -> tuple[
    CreateFn[ConverseResponseTypeDef, StreamOutputChunk],
    str | None,
    list[BedrockMessageParam],
    list[type[BedrockTool]] | None,
    BedrockCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: BedrockRuntimeClient | AsyncBedrockRuntimeClient | None,
    fn: Callable[..., BedrockDynamicConfig]
    | Callable[..., Awaitable[BedrockDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: BedrockDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: BedrockCallParams,
    extract: bool,
) -> tuple[
    AsyncCreateFn[AsyncConverseResponseTypeDef, AsyncStreamOutputChunk]
    | CreateFn[ConverseResponseTypeDef, StreamOutputChunk],
    str | None,
    list[BedrockMessageParam],
    list[type[BedrockTool]] | None,
    BedrockCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, BedrockTool, call_params
    )
    call_kwargs = cast(BedrockCallKwargs, base_call_kwargs)
    messages = cast(list[BaseMessageParam | BedrockMessageParam], messages)
    messages = convert_message_params(messages)
    if messages[0]["role"] == "system":
        call_kwargs["system"] = [
            {"text": text}
            for c in messages.pop(0)["content"]
            if (text := c.get("text"))
        ]

    call_kwargs_tools = call_kwargs.pop("tools", None)
    if json_mode:
        json_mode_content = _utils.json_mode_content(
            tool_types[0] if tool_types else None
        )
        if "text" in messages[-1]["content"][-1]:
            messages[-1]["content"][-1]["text"] += json_mode_content
        else:
            messages[-1]["content"] = [
                *messages[-1]["content"],
                {"text": json_mode_content},
            ]

    else:
        if call_kwargs_tools:
            call_kwargs["toolConfig"] = cast(
                ToolConfigurationTypeDef, {"tools": call_kwargs_tools}
            )
        if extract:
            assert tool_types, "At least one tool must be provided for extraction."
            if "toolConfig" in call_kwargs:
                call_kwargs["toolConfig"]["toolChoice"] = cast(
                    ToolChoiceTypeDef, {"type": "tool", "name": tool_types[0]._name()}
                )

    call_kwargs |= cast(BedrockCallKwargs, {"modelId": model, "messages": messages})

    if client is None:
        client = (
            asyncio.run(_get_async_client())
            if inspect.iscoroutinefunction(fn)
            else _get_sync_client()
        )
    create = (
        get_async_create_fn(
            client.converse, _extract_async_stream_fn(client.converse_stream, model)
        )
        if isinstance(client, AsyncBedrockRuntimeClient)
        else get_create_fn(
            client.converse, _extract_sync_stream_fn(client.converse_stream, model)
        )
    )
    return create, prompt_template, messages, tool_types, call_kwargs
