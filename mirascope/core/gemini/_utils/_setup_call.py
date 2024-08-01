"""This module contains the setup_call function, which is used to set up the"""

import inspect
from typing import Any, Awaitable, Callable, cast

from google.generativeai import GenerativeModel  # type: ignore
from google.generativeai.types import (  # type: ignore
    AsyncGenerateContentResponse,
    ContentDict,
    GenerateContentResponse,
)

from ...base import BaseMessageParam, BaseTool, _utils
from ..call_params import GeminiCallParams
from ..dynamic_config import GeminiDynamicConfig
from ..tool import GeminiTool
from ._convert_message_params import convert_message_params


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
    Callable[..., GenerateContentResponse]
    | Callable[..., Awaitable[AsyncGenerateContentResponse]],
    str,
    list[ContentDict],
    list[type[GeminiTool]] | None,
    dict[str, Any],
]:
    prompt_template, messages, tool_types, call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, GeminiTool, call_params
    )
    messages = cast(list[BaseMessageParam | ContentDict], messages)
    messages = convert_message_params(messages)
    if json_mode:
        generation_config = call_kwargs.get("generation_config", {})
        generation_config["response_mime_type"] = "application/json"
        call_kwargs["generation_config"] = generation_config
        messages[-1]["parts"].append(
            _utils.json_mode_content(tool_types[0] if tool_types else None)
        )
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        tool_config = call_kwargs.get("tool_config", {})
        tool_config["function_calling_config"] = {"mode": "auto"}
        call_kwargs["tool_config"] = tool_config
    call_kwargs |= {"contents": messages}

    if client is None:
        client = GenerativeModel(model_name=model)
    create = (
        client.generate_content_async
        if inspect.iscoroutinefunction(fn)
        else client.generate_content
    )

    return create, prompt_template, messages, tool_types, call_kwargs
