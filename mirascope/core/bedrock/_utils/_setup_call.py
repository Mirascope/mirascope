"""This module contains the setup_call function for Bedrock tools."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable, Coroutine, Generator
from functools import wraps
from typing import Any, ParamSpec, cast, overload

from aiobotocore.session import AioSession, get_session
from boto3.session import Session
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from mypy_boto3_bedrock_runtime.type_defs import (
    ConverseResponseTypeDef,
    ConverseStreamResponseTypeDef,
    ToolChoiceTypeDef,
    ToolConfigurationTypeDef,
)
from types_aiobotocore_bedrock_runtime import (
    BedrockRuntimeClient as AsyncBedrockRuntimeClient,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseResponseTypeDef as AsyncConverseResponseTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseStreamResponseTypeDef as AsyncConverseStreamResponseTypeDef,
)

from ... import BaseMessageParam
from ...base import BaseTool, _utils
from ...base._utils import (
    AsyncCreateFn,
    CreateFn,
    fn_is_async,
    get_async_create_fn,
    get_create_fn,
)
from .._call_kwargs import BedrockCallKwargs
from .._types import (
    AsyncStreamOutputChunk,
    InternalBedrockMessageParam,
    StreamOutputChunk,
)
from ..call_params import BedrockCallParams
from ..dynamic_config import AsyncBedrockDynamicConfig, BedrockDynamicConfig
from ..tool import BedrockTool
from ._convert_message_params import convert_message_params

_P = ParamSpec("_P")


def _extract_sync_stream_fn(
    fn: Callable[_P, ConverseStreamResponseTypeDef], model: str
) -> Callable[_P, Generator[StreamOutputChunk, None, None]]:
    @wraps(fn)
    def _inner(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> Generator[StreamOutputChunk, None, None]:
        response = fn(*args, **kwargs)
        for chunk in response["stream"]:
            yield StreamOutputChunk(
                responseMetadata=response["ResponseMetadata"], model=model, **chunk
            )

    return _inner


def _extract_async_stream_fn(
    fn: Callable[_P, Coroutine[Any, Any, AsyncConverseStreamResponseTypeDef]],
    model: str,
) -> Callable[_P, AsyncGenerator[AsyncStreamOutputChunk, None]]:
    @wraps(fn)
    async def _inner(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> AsyncGenerator[AsyncStreamOutputChunk, None]:
        response = await fn(*args, **kwargs)
        async for chunk in response["stream"]:
            yield AsyncStreamOutputChunk(
                responseMetadata=response["ResponseMetadata"], model=model, **chunk
            )

    return _inner


async def _get_async_client(session: AioSession) -> AsyncBedrockRuntimeClient:
    async with session.create_client("bedrock-runtime") as client:
        return client


@overload
def setup_call(
    *,
    model: str,
    client: AsyncBedrockRuntimeClient | None,
    fn: Callable[..., Awaitable[AsyncBedrockDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AsyncBedrockDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: BedrockCallParams,
    extract: bool,
) -> tuple[
    AsyncCreateFn[AsyncConverseResponseTypeDef, AsyncStreamOutputChunk],
    str | None,
    list[InternalBedrockMessageParam],
    list[type[BedrockTool]] | None,
    BedrockCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: BedrockRuntimeClient | None,
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
    list[InternalBedrockMessageParam],
    list[type[BedrockTool]] | None,
    BedrockCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: BedrockRuntimeClient | AsyncBedrockRuntimeClient | None,
    fn: Callable[..., BedrockDynamicConfig]
    | Callable[..., Awaitable[AsyncBedrockDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: BedrockDynamicConfig | AsyncBedrockDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: BedrockCallParams,
    extract: bool,
) -> tuple[
    AsyncCreateFn[AsyncConverseResponseTypeDef, AsyncStreamOutputChunk]
    | CreateFn[ConverseResponseTypeDef, StreamOutputChunk],
    str | None,
    list[InternalBedrockMessageParam],
    list[type[BedrockTool]] | None,
    BedrockCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, BedrockTool, call_params
    )
    call_kwargs = cast(BedrockCallKwargs, base_call_kwargs)
    messages = cast(list[InternalBedrockMessageParam | BaseMessageParam], messages)
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
        if fn_is_async(fn):
            session = get_session()
            client = asyncio.run(_get_async_client(session))
        else:
            session = Session()
            client = session.client("bedrock-runtime")

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
