"""Utility functions for Mistral convenience wrapper."""
from inspect import isclass
from typing import Any, Callable, Optional, Type, Union

from ..base import BasePrompt, convert_function_to_tool
from .tools import MistralTool


def convert_tools_list_to_mistral_tools(
    tools: Optional[list[Union[Callable, Type[MistralTool]]]],
) -> Optional[list[Type[MistralTool]]]:
    """Converts a list of `Callable` or `MistralTool` instances to a `MistralTool` list.

    Args:
        tools: A list of functions or `MistralTool`s.

    Returns:
        A list of all items converted to `MistralTool` instances.
    """
    if not tools:
        return None
    return [
        tool if isclass(tool) else convert_function_to_tool(tool, MistralTool)
        for tool in tools
    ]


def patch_mistral_kwargs(
    kwargs: dict[str, Any],
    prompt: BasePrompt,
    tools: Optional[list[Type[MistralTool]]],
) -> None:
    """Sets up the kwargs for a Mistral API call.

    Kwargs are parsed as such: messages are formatted to have the required `role` and
    `content` items; tools (if any exist) are parsed into JSON schemas in order to fit
    the OpenAI API; tool choice, if not provided, is set to "auto". Other kwargs are
    left unchanged.

    Args:
        kwargs: The kwargs to patch.
        prompt: The prompt to use.
        tools: The tools to use, if any.

    """
    kwargs["messages"] = prompt.messages
    kwargs.update(
        {
            key: value
            for key, value in prompt.call_params.model_dump(
                exclude={"tools", "model", "wrapper", "async_wrapper", "endpoint"}
            ).items()
            if value is not None
        }
    )

    if tools:
        kwargs["tools"] = [tool.tool_schema() for tool in tools]
        if "tool_choice" not in kwargs:
            kwargs["tool_choice"] = "auto"
