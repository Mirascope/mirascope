"""Utility functions for OpenAIChat."""
from inspect import isclass
from typing import Any, Callable, Optional, Type, Union, cast

from openai.types.chat import ChatCompletionUserMessageParam
from pydantic import BaseModel, create_model

from ...prompts import Prompt
from ...prompts.tools import convert_function_to_tool
from .tools import OpenAITool


def convert_tools_list_to_openai_tools(
    tools: Optional[list[Union[Callable, Type[OpenAITool]]]],
) -> Optional[list[Type[OpenAITool]]]:
    """Converts a list of `Callable` or `OpenAITool` instances to an `OpenAITool` list.

    Args:
        tools: A list of functions or `OpenAITool`s.

    Returns:
        A list of all items converted to `OpenAITool` instances.
    """
    if not tools:
        return None
    return [
        tool if isclass(tool) else convert_function_to_tool(tool, OpenAITool)
        for tool in tools
    ]


def patch_openai_kwargs(
    kwargs: dict[str, Any],
    prompt: Optional[Union[Prompt, str]],
    tools: Optional[list[Type[OpenAITool]]],
) -> None:
    """Sets up the kwargs for an OpenAI API call.

    Kwargs are parsed as such: messages are formatted to have the required `role` and
    `content` items; tools (if any exist) are parsed into JSON schemas in order to fit
    the OpenAI API; tool choice, if not provided, is set to "auto". Other kwargs are
    left unchanged.

    Args:
        kwargs: The kwargs to patch.
        prompt: The prompt to use.
        tools: The tools to use, if any.

    Raises:
        ValueError: if neither `prompt` nor `messages` are provided.
    """
    if prompt is None:
        if "messages" not in kwargs:
            raise ValueError("Either `prompt` or `messages` must be provided.")
    elif isinstance(prompt, str):
        kwargs["messages"] = [
            ChatCompletionUserMessageParam(role="user", content=prompt)
        ]
    else:
        kwargs["messages"] = prompt.messages
        kwargs.update(
            {
                key: value
                for key, value in prompt.call_params.model_dump(
                    exclude={"tools", "model"}
                ).items()
                if value is not None
            }
        )

    if tools:
        kwargs["tools"] = [tool.tool_schema() for tool in tools]
        if "tool_choice" not in kwargs:
            kwargs["tool_choice"] = "auto"
