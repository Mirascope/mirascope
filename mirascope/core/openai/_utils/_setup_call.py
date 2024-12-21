"""This module contains the setup_call function for OpenAI tools."""

import inspect
import warnings
from collections.abc import Awaitable, Callable
from typing import Any, cast, overload

from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import (
    DEFAULT_TOOL_DOCSTRING,
    AsyncCreateFn,
    CreateFn,
    get_async_create_fn,
    get_create_fn,
)
from ...base.call_params import CommonCallParams
from ...base.stream_config import StreamConfig
from .._call_kwargs import OpenAICallKwargs
from ..call_params import OpenAICallParams
from ..dynamic_config import AsyncOpenAIDynamicConfig, OpenAIDynamicConfig
from ..tool import GenerateOpenAIStrictToolJsonSchema, OpenAITool
from ._convert_common_call_params import convert_common_call_params
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: AsyncOpenAI | AsyncAzureOpenAI | None,
    fn: Callable[..., Awaitable[AsyncOpenAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: AsyncOpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    AsyncCreateFn[ChatCompletion, ChatCompletionChunk],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: OpenAI | AzureOpenAI | None,
    fn: Callable[..., OpenAIDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: OpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    CreateFn[ChatCompletion, ChatCompletionChunk],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: OpenAI | AsyncOpenAI | AzureOpenAI | AsyncAzureOpenAI | None,
    fn: Callable[..., OpenAIDynamicConfig]
    | Callable[..., Awaitable[AsyncOpenAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: OpenAIDynamicConfig | AsyncOpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    CreateFn[ChatCompletion, ChatCompletionChunk]
    | AsyncCreateFn[ChatCompletion, ChatCompletionChunk],
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn,
        fn_args,
        dynamic_config,
        tools,
        OpenAITool,
        call_params,
        convert_common_call_params,
    )
    call_kwargs = cast(OpenAICallKwargs, base_call_kwargs)
    messages = cast(list[BaseMessageParam | ChatCompletionMessageParam], messages)
    messages = convert_message_params(messages)
    if json_mode:
        if response_model and response_model.model_config.get("strict", False):
            call_kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "description": response_model.__doc__ or DEFAULT_TOOL_DOCSTRING,
                    "strict": True,
                    "schema": response_model.model_json_schema(
                        schema_generator=GenerateOpenAIStrictToolJsonSchema
                    ),
                },
            }
        else:
            call_kwargs["response_format"] = {"type": "json_object"}
            json_mode_content = _utils.json_mode_content(response_model).strip()
            messages.append(
                ChatCompletionUserMessageParam(role="user", content=json_mode_content)
            )
    elif response_model:
        assert tool_types, "At least one tool must be provided for extraction."
        if tool_types and tool_types[0].model_config.get("strict", False):
            warnings.warn(
                "You must set `json_mode=True` to use `strict=True` response models. "
                "Ignoring `strict` and using tools for extraction.",
                UserWarning,
            )
        call_kwargs["tool_choice"] = "required"
    if stream:
        call_kwargs["stream_options"] = (
            {"include_usage": True}
            if "stream_options" not in call_kwargs
            else call_kwargs["stream_options"].update({"include_usage": True})  # pyright: ignore [reportOptionalMemberAccess]
        )
    call_kwargs |= {"model": model, "messages": messages}

    if client is None:
        client = AsyncOpenAI() if inspect.iscoroutinefunction(fn) else OpenAI()
    create = (
        get_async_create_fn(client.chat.completions.create)
        if isinstance(client, AsyncOpenAI)
        else get_create_fn(client.chat.completions.create)
    )
    return create, prompt_template, messages, tool_types, call_kwargs
