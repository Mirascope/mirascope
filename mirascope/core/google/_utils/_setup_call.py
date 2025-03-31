"""This module contains the setup_call function, which is used to set up the"""

import contextlib
from collections.abc import Awaitable, Callable, Generator
from typing import Any, cast, overload

from google.genai import Client
from google.genai.types import (
    ContentDict,
    FunctionCallingConfig,
    FunctionCallingConfigMode,
    GenerateContentConfig,
    GenerateContentConfigDict,
    GenerateContentResponse,
    Part,
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


def _get_generate_content_config(
    config: GenerateContentConfig | GenerateContentConfigDict,
) -> GenerateContentConfig:
    if isinstance(config, dict):
        return GenerateContentConfig.model_validate(config)
    return config


@contextlib.contextmanager
def _generate_content_config_context(
    call_kwargs: GoogleCallKwargs,
) -> Generator[GenerateContentConfig, None, None]:
    config = call_kwargs.get("config", {})
    config = _get_generate_content_config(config)
    yield config
    call_kwargs["config"] = config


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

    if client is None:
        client = Client()

    messages = convert_message_params(messages, client)

    if messages[0] and messages[0].get("role") == "system":
        with _generate_content_config_context(call_kwargs) as config:
            system_message = messages.pop(0)
            message_parts = system_message.get("parts", [])
            if message_parts:
                config.system_instruction = [
                    Part.model_validate(part) for part in message_parts
                ]

    if json_mode:
        with _generate_content_config_context(call_kwargs) as config:
            if not tools:
                config.response_mime_type = "application/json"
        messages[-1]["parts"].append(  # pyright: ignore [reportTypedDictNotRequiredAccess, reportOptionalMemberAccess, reportArgumentType]
            PartDict(text=_utils.json_mode_content(response_model))
        )  # pyright: ignore [reportTypedDictNotRequiredAccess, reportOptionalMemberAccess, reportArgumentType]
    elif response_model:
        assert tool_types, "At least one tool must be provided for extraction."
        with _generate_content_config_context(call_kwargs) as config:
            config.tool_config = ToolConfig(
                function_calling_config=FunctionCallingConfig(
                    mode=FunctionCallingConfigMode.ANY,
                    allowed_function_names=[tool_types[0]._name()],
                )
            )
    config_tools = call_kwargs.pop("tools", None)
    if config_tools:
        with _generate_content_config_context(call_kwargs) as config:
            config.tools = cast(ToolListUnion, config_tools)

    call_kwargs |= {"model": model, "contents": messages}

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
    if client.vertexai:
        if isinstance(dynamic_config, dict):
            metadata = dynamic_config.get("metadata", {})
            tags = metadata.get("tags", set())
            tags.add("use_vertex_ai")
            metadata["tags"] = tags
            dynamic_config["metadata"] = metadata
        else:
            metadata = getattr(fn, "_metadata", {})
            tags = metadata.get("tags", set())
            tags.add("use_vertex_ai")
            metadata["tags"] = tags
            fn._metadata = metadata

    return (
        create,
        prompt_template,
        messages,
        tool_types,
        call_kwargs,
    )
