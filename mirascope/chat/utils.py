"""Utility functions for mirascope chat."""

from inspect import Parameter, signature
from typing import Any, Callable, Type, cast

from docstring_parser import parse
from openai.types.chat import ChatCompletionMessageParam
from pydantic import create_model
from pydantic.fields import FieldInfo

from ..prompts import Prompt
from .tools import OpenAITool, openai_tool_fn


def get_openai_chat_messages(
    prompt: Prompt,
) -> list[ChatCompletionMessageParam]:
    """Returns a list of messages parsed from the prompt."""
    return [
        cast(ChatCompletionMessageParam, {"role": role, "content": content})
        for role, content in prompt.messages
    ]


def convert_function_to_openai_tool(fn: Callable) -> Type[OpenAITool]:
    """Constructs and `OpenAITool` type from the given function.

    Args:
        fn: The function to convert.

    Returns:
        The constructed `OpenAITool` type.

    Raises:
        ValueError: if the given function doesn't have a docstring.
        ValueError: if the given function's parameters don't have type annotations.
        ValueError: if the given function's parameter names don't match the docstring's
            parameter names.
        ValueError: if the given function's parameters don't have dosctring
            descriptions.
    """
    if not fn.__doc__:
        raise ValueError("Function must have a docstring.")

    docstring = parse(fn.__doc__)

    doc = ""
    if docstring.short_description:
        doc = docstring.short_description
    if docstring.long_description:
        doc += "\n\n" + docstring.long_description

    field_definitions = {}
    for i, parameter in enumerate(signature(fn).parameters.values()):
        if parameter.annotation == Parameter.empty:
            raise ValueError("All parameters must have a type annotation.")

        docstring_param = docstring.params[i]
        if docstring_param.arg_name != parameter.name:
            raise ValueError(
                f"Function parameter name {parameter.name} does not match docstring "
                f"parameter name {docstring_param.arg_name}. Make sure that the "
                "parameter names match exactly."
            )
        if not docstring_param.description:
            raise ValueError("All parameters must have a description.")

        field_info = {"description": docstring.params[i].description}
        if parameter.default != Parameter.empty:
            field_info["default"] = parameter.default

        field_definitions[parameter.name] = (
            parameter.annotation,
            FieldInfo(**field_info),  # type: ignore
        )

    return create_model(
        "".join(word.title() for word in fn.__name__.split("_")),
        __base__=openai_tool_fn(fn)(OpenAITool),
        __doc__=doc,
        **cast(dict[str, Any], field_definitions),
    )
