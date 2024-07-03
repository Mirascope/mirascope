"""This module contains the setup_call function for Groq tools."""

import inspect
from typing import Any, Awaitable, Callable

from groq import AsyncGroq, Groq
from groq.types.chat import ChatCompletion, ChatCompletionMessageParam

from ...base import BaseTool, _utils
from ..call_params import GroqCallParams
from ..dynamic_config import GroqDynamicConfig
from ..tool import GroqTool


def setup_call(
    *,
    model: str,
    client: Groq | AsyncGroq | None,
    fn: Callable[..., GroqDynamicConfig | Awaitable[GroqDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: GroqDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: GroqCallParams,
    extract: bool,
) -> tuple[
    Callable[..., ChatCompletion] | Callable[..., Awaitable[ChatCompletion]],
    str,
    list[ChatCompletionMessageParam],
    list[type[GroqTool]] | None,
    dict[str, Any],
]:
    prompt_template, messages, tool_types, call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, GroqTool, call_params
    )
    if client is None:
        client = AsyncGroq() if inspect.iscoroutinefunction(fn) else Groq()
    create = client.chat.completions.create
    call_kwargs |= {"model": model, "messages": messages}
    if json_mode:
        call_kwargs["response_format"] = {"type": "json_object"}
        messages[-1]["content"] += _utils.json_mode_content(
            tool_types[0] if tool_types else None
        )
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        call_kwargs["tool_choice"] = {
            "type": "function",
            "function": {"name": tool_types[0]._name()},
        }

    return create, prompt_template, messages, tool_types, call_kwargs  # type: ignore
