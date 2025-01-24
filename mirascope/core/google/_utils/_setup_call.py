"""This module contains the setup_call function, which is used to set up the"""

from collections.abc import Awaitable, Callable
from typing import Any, cast, overload

from google.genai import Client
from google.genai.types import (
    ContentDict,
    FunctionCallingConfig,
    FunctionCallingConfigMode,
    GenerateContentConfig,
    GenerateContentResponse,
    PartDict,
    ToolConfig,
    ToolListUnion,
)
from pydantic import BaseModel

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import (
    AsyncCreateFn,
    CreateFn,
    fn_is_async,
    get_async_create_fn,
    get_create_fn,
)
from ...base.call_params import CommonCallParams
from ...base.stream_config import StreamConfig
from .._call_kwargs import GoogleCallKwargs
from ..call_params import GoogleCallParams
from ..dynamic_config import GoogleDynamicConfig
from ..tool import GoogleTool
from ._convert_common_call_params import convert_common_call_params
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: Client | None,
    fn: Callable[..., Awaitable[GoogleDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: GoogleDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: GoogleCallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    AsyncCreateFn[GenerateContentResponse, GenerateContentResponse],
    str | None,
    list[ContentDict],
    list[type[GoogleTool]] | None,
    GoogleCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: Client | None,
    fn: Callable[..., GoogleDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: GoogleDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: GoogleCallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    CreateFn[GenerateContentResponse, GenerateContentResponse],
    str | None,
    list[ContentDict],
    list[type[GoogleTool]] | None,
    GoogleCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: Client | None,
    fn: Callable[..., GoogleDynamicConfig | Awaitable[GoogleDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: GoogleDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: GoogleCallParams | CommonCallParams,
    response_model: type[BaseModel] | None,
    stream: bool | StreamConfig,
) -> tuple[
    CreateFn[GenerateContentResponse, GenerateContentResponse]
    | AsyncCreateFn[GenerateContentResponse, GenerateContentResponse],
    str | None,
    list[ContentDict],
    list[type[GoogleTool]] | None,
    GoogleCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn,
        fn_args,
        dynamic_config,
        tools,
        GoogleTool,
        call_params,
        convert_common_call_params,
    )
    call_kwargs = cast(GoogleCallKwargs, base_call_kwargs)
    messages = cast(list[BaseMessageParam | ContentDict], messages)
    messages = convert_message_params(messages)
    if json_mode:
        config = call_kwargs.get("config", {})
        if isinstance(config, dict):
            config = GenerateContentConfig.model_validate(config)
        if not tools:
            config.response_mime_type = "application/json"
        call_kwargs["config"] = config
        messages[-1]["parts"].append(  # pyright: ignore [reportTypedDictNotRequiredAccess, reportOptionalMemberAccess, reportArgumentType]
            PartDict(text=_utils.json_mode_content(response_model))
        )  # pyright: ignore [reportTypedDictNotRequiredAccess, reportOptionalMemberAccess, reportArgumentType]
    elif response_model:
        assert tool_types, "At least one tool must be provided for extraction."
        config = call_kwargs.get("config", {})
        if isinstance(config, dict):
            config = GenerateContentConfig.model_validate(config)
        config.tool_config = ToolConfig(
            function_calling_config=FunctionCallingConfig(
                mode=FunctionCallingConfigMode.ANY,
                allowed_function_names=[tool_types[0]._name()],
            )
        )
        call_kwargs["config"] = config
    config_tools = call_kwargs.pop("tools", None)
    if config_tools:
        config = call_kwargs.get("config", {})
        if isinstance(config, dict):
            config = GenerateContentConfig.model_validate(config)
        config.tools = cast(ToolListUnion, config_tools)
        call_kwargs["config"] = config
    call_kwargs |= {"model": model, "contents": messages}

    if client is None:
        client = Client()

    create = (
        get_async_create_fn(
            client.aio.models.generate_content,
            client.aio.models.generate_content_stream,
        )
        if fn_is_async(fn)
        else get_create_fn(
            client.models.generate_content, client.models.generate_content_stream
        )
    )

    return create, prompt_template, messages, tool_types, call_kwargs
