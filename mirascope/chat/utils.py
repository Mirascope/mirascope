"""Utility functions for mirascope chat."""
from inspect import Parameter, isclass, signature
from typing import Any, Callable, Optional, Type, Union, cast, get_type_hints

from docstring_parser import parse
from openai.types.chat import ChatCompletionUserMessageParam
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from ..prompts import Prompt
from .tools import OpenAITool, openai_tool_fn


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
        tool if isclass(tool) else convert_function_to_openai_tool(tool)
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
                for key, value in prompt._call_params.model_dump(
                    exclude={"tools", "model"}
                ).items()
                if value is not None
            }
        )

    if tools:
        kwargs["tools"] = [tool.tool_schema() for tool in tools]
        if "tool_choice" not in kwargs:
            kwargs["tool_choice"] = "auto"


def convert_function_to_openai_tool(fn: Callable) -> Type[OpenAITool]:
    """Constructs an `OpenAITool` type from the given function.

    This method expects all function parameters to be properly documented in identical
    order with identical variable names, as well as descriptions of each parameter.
    Errors will be raised if any of these conditions are not met.

    Args:
        fn: The function to convert.

    Returns:
        The constructed `OpenAITool` type.

    Raises:
        ValueError: if the given function doesn't have a docstring.
        ValueError: if the given function's parameters don't have type annotations.
        ValueError: if a given function's parameter is in the docstring args section but
            the name doesn't match the docstring's parameter name.
        ValueError: if a given function's parameter is in the docstring args section but
            doesn't have a dosctring description.
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
    hints = get_type_hints(fn)
    for i, parameter in enumerate(signature(fn).parameters.values()):
        if parameter.name == "self" or parameter.name == "cls":
            continue
        if parameter.annotation == Parameter.empty:
            raise ValueError("All parameters must have a type annotation.")

        docstring_description = None
        if i < len(docstring.params):
            docstring_param = docstring.params[i]
            if docstring_param.arg_name != parameter.name:
                raise ValueError(
                    f"Function parameter name {parameter.name} does not match docstring "
                    f"parameter name {docstring_param.arg_name}. Make sure that the "
                    "parameter names match exactly."
                )
            if not docstring_param.description:
                raise ValueError("All parameters must have a description.")
            docstring_description = docstring_param.description

        field_info = FieldInfo(annotation=hints[parameter.name])
        if parameter.default != Parameter.empty:
            field_info.default = parameter.default
        if docstring_description:  # we check falsy here because this comes from docstr
            field_info.description = docstring_description

        param_name = parameter.name
        if param_name.startswith("model_"):  # model_ is a BaseModel reserved namespace
            param_name = "aliased_" + param_name
            field_info.alias = parameter.name
            field_info.validation_alias = parameter.name
            field_info.serialization_alias = parameter.name

        field_definitions[param_name] = (
            hints[parameter.name],
            field_info,
        )

    return create_model(
        "".join(word.title() for word in fn.__name__.split("_")),
        __base__=openai_tool_fn(fn)(OpenAITool),
        __doc__=doc,
        **cast(dict[str, Any], field_definitions),
    )


def convert_base_model_to_openai_tool(schema: Type[BaseModel]) -> Type[OpenAITool]:
    """Converts a `BaseModel` schema to an `OpenAITool` instance.

    By adding a docstring (if needed) and passing on fields and field information in
    dictionary format, a Pydantic `BaseModel` can be converted into an `OpenAITool` for
    performing extraction.

    Args:
        schema: The `BaseModel` schema to convert.

    Returns:
        The constructed `OpenAITool` instance.
    """
    internal_doc = (
        f"An `{schema.__name__}` instance with all correctly typed parameters "
        "extracted from the completion. Must include required parameters and may "
        "exclude optional parameters unless present in the text."
    )
    field_definitions = {
        field_name: (field_info.annotation, field_info)
        for field_name, field_info in schema.model_fields.items()
    }
    return create_model(
        f"{schema.__name__}Tool",
        __base__=OpenAITool,
        __doc__=schema.__doc__ if schema.__doc__ else internal_doc,
        **cast(dict[str, Any], field_definitions),
    )
