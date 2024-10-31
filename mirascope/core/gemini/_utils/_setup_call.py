"""This module contains the setup_call function, which is used to set up the"""

from collections.abc import Awaitable, Callable
from dataclasses import asdict, is_dataclass
from typing import Any, cast, overload

from google.generativeai import GenerativeModel
from google.generativeai.types import (
    AsyncGenerateContentResponse,
    ContentDict,
    GenerateContentResponse,
    GenerationConfigDict,
)
from google.generativeai.types.content_types import ToolConfigDict

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import (
    AsyncCreateFn,
    CreateFn,
    fn_is_async,
    get_async_create_fn,
    get_create_fn,
)
from .._call_kwargs import GeminiCallKwargs
from ..call_params import GeminiCallParams
from ..dynamic_config import GeminiDynamicConfig
from ..tool import GeminiTool
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: GenerativeModel | None,
    fn: Callable[..., Awaitable[GeminiDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: GeminiDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: GeminiCallParams,
    extract: bool = False,
) -> tuple[
    AsyncCreateFn[AsyncGenerateContentResponse, AsyncGenerateContentResponse],
    str | None,
    list[ContentDict],
    list[type[GeminiTool]] | None,
    GeminiCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: GenerativeModel | None,
    fn: Callable[..., GeminiDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: GeminiDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: GeminiCallParams,
    extract: bool = False,
) -> tuple[
    CreateFn[GenerateContentResponse, GenerateContentResponse],
    str | None,
    list[ContentDict],
    list[type[GeminiTool]] | None,
    GeminiCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: GenerativeModel | None,
    fn: Callable[..., GeminiDynamicConfig | Awaitable[GeminiDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: GeminiDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: GeminiCallParams,
    extract: bool = False,
) -> tuple[
    CreateFn[GenerateContentResponse, GenerateContentResponse]
    | AsyncCreateFn[AsyncGenerateContentResponse, AsyncGenerateContentResponse],
    str | None,
    list[ContentDict],
    list[type[GeminiTool]] | None,
    GeminiCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, GeminiTool, call_params
    )
    call_kwargs = cast(GeminiCallKwargs, base_call_kwargs)
    messages = cast(list[BaseMessageParam | ContentDict], messages)
    messages = convert_message_params(messages)
    if json_mode:
        generation_config = call_kwargs.get("generation_config", {})
        if is_dataclass(generation_config):
            generation_config = asdict(generation_config)
        generation_config["response_mime_type"] = "application/json"
        call_kwargs["generation_config"] = cast(GenerationConfigDict, generation_config)
        messages[-1]["parts"].append(
            _utils.json_mode_content(tool_types[0] if tool_types else None)
        )
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        call_kwargs.pop("tool_config", None)
        tool_config = ToolConfigDict()
        tool_config.function_calling_config = {
            "mode": "any",
            "allowed_function_names": [tool_types[0]._name()],
        }
        call_kwargs["tool_config"] = tool_config
    call_kwargs |= {"contents": messages}

    if client is None:
        client = GenerativeModel(model_name=model)

    create = (
        get_async_create_fn(client.generate_content_async)
        if fn_is_async(fn)
        else get_create_fn(client.generate_content)
    )

    return create, prompt_template, messages, tool_types, call_kwargs
