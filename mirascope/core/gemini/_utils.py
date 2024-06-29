"""Utilities for the Mirascope Core OpenAI module."""

import inspect
import json
from textwrap import dedent
from typing import Any, Awaitable, Callable

from google.generativeai import GenerativeModel  # type: ignore
from google.generativeai.types import (  # type: ignore
    ContentsType,
    GenerateContentResponse,
)

from ..base import BaseTool, _utils
from .call_params import GeminiCallParams
from .dynamic_config import GeminiDynamicConfig
from .tool import GeminiTool


def setup_call(
    model: str,
    client: object | None,
    fn: Callable[..., GeminiDynamicConfig | Awaitable[GeminiDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: GeminiDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    call_params: GeminiCallParams,
) -> tuple[
    Callable[..., GenerateContentResponse],
    str,
    list[dict[str, ContentsType]],
    list[type[GeminiTool]],
    dict[str, Any],
]:
    prompt_template, messages, tool_types, call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, GeminiTool, call_params
    )

    gemini_messages = []
    for message in messages:
        if (role := message["role"]) == "system":
            gemini_messages += [
                {
                    "role": "user",
                    "parts": [message["content"]],
                },
                {
                    "role": "model",
                    "parts": ["Ok! I will adhere to this system message."],
                },
            ]
        else:
            gemini_messages.append({"role": role, "parts": [message["content"]]})

    if client is None:
        client = GenerativeModel(model_name=model)
    create = (
        client.generate_content_async
        if inspect.iscoroutinefunction(fn)
        else client.generate_content
    )
    call_kwargs |= {"contents": gemini_messages}

    return create, prompt_template, gemini_messages, tool_types, call_kwargs


def setup_extract(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: GeminiDynamicConfig,
    tool: type[BaseTool],
    call_params: GeminiCallParams,
) -> tuple[
    bool,
    list[ContentsType],
    GeminiCallParams,
]:
    _, messages, [tool_type], call_kwargs = setup_call(
        fn, fn_args, fn_return, [tool], call_params
    )
    if json_mode := bool(
        (generation_config := call_kwargs.get("generation_config", None))
        and generation_config.get("response_mime_type", "") == "application/json"
    ):
        messages.append(
            {
                "role": "user",
                "parts": [
                    dedent(
                        f"""\
            Extract a valid JSON object instance from the content using this schema:

            {json.dumps(tool_type.model_json_schema(), indent=2)}"""
                    )
                ],
            }
        )
        call_kwargs["tools"] = None  # type: ignore
    else:
        call_kwargs["tools"] = [tool_type.tool_schema()]  # type: ignore
        tool_config = call_kwargs.get("tool_config", {})
        tool_config["function_calling_config"] = {"mode": "auto"}
        call_kwargs["tool_config"] = tool_config

    return json_mode, messages, call_kwargs
