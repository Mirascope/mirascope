"""This module contains the setup_call function for Bedrock tools."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator, Awaitable, Callable, Coroutine, Generator
from functools import wraps
from typing import Any, ParamSpec, cast, overload

import aiobotocore.client
from aiobotocore.session import AioSession, get_session
from boto3.session import Session
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from mypy_boto3_bedrock_runtime.type_defs import (
    ConverseResponseTypeDef,
    ConverseStreamResponseTypeDef,
    ToolChoiceTypeDef,
    ToolConfigurationTypeDef,
)
from pydantic import BaseModel
from types_aiobotocore_bedrock_runtime import (
    BedrockRuntimeClient as AsyncBedrockRuntimeClient,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseRequestRequestTypeDef as AsyncConverseRequestRequestTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseResponseTypeDef as AsyncConverseResponseTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseStreamRequestRequestTypeDef as AsyncConverseStreamRequestRequestTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseStreamResponseTypeDef as AsyncConverseStreamResponseTypeDef,
)
from typing_extensions import Unpack

from ... import BaseMessageParam
from ...base import BaseTool, _utils
from ...base._utils import (
    AsyncCreateFn,
    CreateFn,
    fn_is_async,
    get_async_create_fn,
    get_create_fn,
)
from ...base.call_params import CommonCallParams
from ...base.stream_config import StreamConfig
from .._call_kwargs import BedrockCallKwargs
from .._types import (
    AsyncStreamOutputChunk,
    InternalBedrockMessageParam,
    StreamOutputChunk,
)
from ..call_params import BedrockCallParams
from ..dynamic_config import AsyncBedrockDynamicConfig, BedrockDynamicConfig
from ..tool import BedrockTool
from ._convert_common_call_params import convert_common_call_params
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


class _AsyncBedrockRuntimeWrappedClient:
    def __init__(self, session: AioSession, model: str) -> None:
        self.session: AioSession = session
        self.model: str = model

    async def converse(
        self, **kwargs: Unpack[AsyncConverseRequestRequestTypeDef]
    ) -> AsyncConverseResponseTypeDef:
        async with self.session.create_client("bedrock-runtime") as client:
            return await client.converse(**kwargs)

    async def converse_stream(
        self, **kwargs: Unpack[AsyncConverseStreamRequestRequestTypeDef]
    ) -> AsyncGenerator[AsyncStreamOutputChunk, None]:
        async with self.session.create_client("bedrock-runtime") as client:
            response = await client.converse_stream(**kwargs)
            async for chunk in response["stream"]:
                yield AsyncStreamOutputChunk(
                    responseMetadata=response["ResponseMetadata"],
                    model=self.model,
                    **chunk,
                )


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
    call_params: BedrockCallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
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
    call_params: BedrockCallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
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
    call_params: BedrockCallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    AsyncCreateFn[AsyncConverseResponseTypeDef, AsyncStreamOutputChunk]
    | CreateFn[ConverseResponseTypeDef, StreamOutputChunk],
    str | None,
    list[InternalBedrockMessageParam],
    list[type[BedrockTool]] | None,
    BedrockCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn,
        fn_args,
        dynamic_config,
        tools,
        BedrockTool,
        call_params,
        convert_common_call_params,
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

    if call_kwargs_tools := call_kwargs.pop("tools", None):
        call_kwargs["toolConfig"] = cast(
            ToolConfigurationTypeDef, {"tools": call_kwargs_tools}
        )
    if json_mode:
        json_mode_content = _utils.json_mode_content(response_model)
        if "text" in messages[-1]["content"][-1]:
            messages[-1]["content"][-1]["text"] += json_mode_content
        else:
            messages[-1]["content"] = [
                *messages[-1]["content"],
                {"text": json_mode_content},
            ]
    elif response_model:
        assert tool_types, "At least one tool must be provided for extraction."
        if "toolConfig" in call_kwargs:
            call_kwargs["toolConfig"]["toolChoice"] = cast(
                ToolChoiceTypeDef, {"tool": {"name": tool_types[0]._name()}}
            )

    call_kwargs |= cast(BedrockCallKwargs, {"modelId": model, "messages": messages})

    env_vars = {}
    if access_key_id := os.getenv("AWS_ACCESS_KEY_ID"):
        env_vars["aws_access_key_id"] = access_key_id
    if secret_access_key := os.getenv("AWS_SECRET_ACCESS_KEY"):
        env_vars["aws_secret_access_key"] = secret_access_key
    if session_token := os.getenv("AWS_SESSION_TOKEN"):
        env_vars["aws_session_token"] = session_token
    if region_name := os.getenv("AWS_REGION_NAME"):
        env_vars["region_name"] = region_name
    if profile_name := os.getenv("AWS_PROFILE"):
        env_vars["profile_name"] = profile_name
    if client is None:
        if fn_is_async(fn):
            session = get_session(env_vars=env_vars)
            _client = _AsyncBedrockRuntimeWrappedClient(session, model)
        else:
            session = Session(**env_vars)
            _client = session.client("bedrock-runtime")
    else:
        _client = client
    if isinstance(_client, aiobotocore.client.AioBaseClient):
        create = get_async_create_fn(
            _client.converse, _extract_async_stream_fn(_client.converse_stream, model)
        )
    elif isinstance(_client, _AsyncBedrockRuntimeWrappedClient):
        create = get_async_create_fn(_client.converse, _client.converse_stream)

    else:
        create = get_create_fn(
            _client.converse, _extract_sync_stream_fn(_client.converse_stream, model)
        )
    return create, prompt_template, messages, tool_types, call_kwargs
