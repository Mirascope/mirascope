"""Internal Utilities."""

import inspect
import re
from abc import update_abstractmethods
from enum import Enum
from string import Formatter
from textwrap import dedent
from typing import (
    Annotated,
    Any,
    Callable,
    Literal,
    ParamSpec,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from docstring_parser import parse
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from .message_param import BaseMessageParam

DEFAULT_TOOL_DOCSTRING = """\
Correctly formatted and typed parameters extracted from the completion. \
Must include required parameters and may exclude optional parameters unless present in the text.\
"""


def get_template_variables(template: str) -> list[str]:
    """Returns the variables in the given template string."""
    return [var for _, var, _, _ in Formatter().parse(template) if var is not None]


def get_template_values(
    template_variables: list[str], attrs: dict[str, Any]
) -> dict[str, Any]:
    """Returns the values of the given `template_variables` from the provided `attrs`."""
    values = {}
    if "self" in attrs:
        values["self"] = attrs.get("self")
    for var in template_variables:
        if var.startswith("self"):
            continue
        attr = attrs[var]
        if isinstance(attr, list):
            if len(attr) == 0:
                values[var] = ""
            elif isinstance(attr[0], list):
                values[var] = "\n\n".join(
                    ["\n".join([str(subitem) for subitem in item]) for item in attr]
                )
            else:
                values[var] = "\n".join([str(item) for item in attr])
        else:
            values[var] = str(attr)
    return values


def format_prompt_template(template: str, attrs: dict[str, Any]) -> str:
    """Formats the given prompt `template`"""
    dedented_template = dedent(template).strip()
    template_vars = get_template_variables(dedented_template)

    values = get_template_values(template_vars, attrs)

    return dedented_template.format(**values)


def parse_prompt_messages(
    roles: list[str], template: str, attrs: dict[str, Any]
) -> list[BaseMessageParam | Any]:
    """Returns messages parsed from the provided prompt `template`.

    Raises:
        ValueError: if `MESSAGES` keyword is used with a non-list attribute.
    """
    messages = []
    re_roles = "|".join([role.upper() for role in roles] + ["MESSAGES"])
    for match in re.finditer(rf"({re_roles}):((.|\n)+?)(?=({re_roles}):|\Z)", template):
        role = match.group(1).lower()
        if role == "messages":
            template_var = [
                var
                for _, var, _, _ in Formatter().parse(match.group(2))
                if var is not None
            ][0]
            if template_var.startswith("self"):
                if "self" not in attrs:
                    raise ValueError(
                        "MESSAGES keyword used with `self.` but `self` was not found."
                    )
                attr = getattr(attrs["self"], template_var[5:])
            else:
                attr = attrs[template_var]
            if attr is None or not isinstance(attr, list):
                raise ValueError(
                    f"MESSAGES keyword used with attribute `{template_var}`, which "
                    "is not a `list` of messages."
                )
            messages += attr
        else:
            content = format_prompt_template(match.group(2), attrs)
            if content:
                messages.append({"role": role, "content": content})
    if len(messages) == 0:
        messages.append(
            {
                "role": "user",
                "content": format_prompt_template(template, attrs),
            }
        )
    return messages


P = ParamSpec("P")
R = TypeVar("R")
BaseToolT = TypeVar("BaseToolT", bound=BaseModel)


def convert_function_to_base_tool(
    fn: Callable, base: type[BaseToolT], __doc__: str | None = None
) -> type[BaseToolT]:
    """Constructst a `BaseToolT` type from the given function.

    This method expects all function parameters to be properly documented in identical
    order with identical variable names, as well as descriptions of each parameter.
    Errors will be raised if any of these conditions are not met.

    Args:
        fn: The function to convert.
        base: The `BaseToolT` type to which the function is converted.
        __doc__: The docstring to use for the constructed `BaseToolT` type.

    Returns:
        The constructed `BaseToolT` type.

    Raises:
        ValueError: if the given function's parameters don't have type annotations.
        ValueError: if a given function's parameter is in the docstring args section but
            the name doesn't match the docstring's parameter name.
        ValueError: if a given function's parameter is in the docstring args section but
            doesn't have a docstring description.
    """
    docstring = None
    func_doc = __doc__ or fn.__doc__
    if func_doc:
        docstring = parse(func_doc)

    field_definitions = {}
    hints = get_type_hints(fn)
    for i, parameter in enumerate(inspect.signature(fn).parameters.values()):
        if parameter.name == "self" or parameter.name == "cls":
            continue
        if parameter.annotation == inspect.Parameter.empty:
            raise ValueError("All parameters must have a type annotation.")

        docstring_description = None
        if docstring and i < len(docstring.params):
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
        if parameter.default != inspect.Parameter.empty:
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

    model = create_model(
        fn.__name__,
        __base__=base,
        __doc__=inspect.cleandoc(func_doc) if func_doc else DEFAULT_TOOL_DOCSTRING,
        **cast(dict[str, Any], field_definitions),
    )

    def call(self: base):
        return fn(
            **{
                str(
                    self.model_fields[field_name].alias
                    if self.model_fields[field_name].alias
                    else field_name
                ): getattr(self, field_name)
                for field_name in self.model_dump(exclude={"tool_call"})
            }
        )

    setattr(model, "call", call)
    return update_abstractmethods(model)


def convert_base_model_to_base_tool(
    model: type[BaseModel], base: type[BaseToolT]
) -> type[BaseToolT]:
    """Converts a `BaseModel` schema to a `BaseToolT` type.

    By adding a docstring (if needed) and passing on fields and field information in
    dictionary format, a Pydantic `BaseModel` can be converted into an `BaseTool` for
    performing extraction.

    Args:
        schema: The `BaseModel` schema to convert.

    Returns:
        The constructed `BaseModelT` type.
    """
    field_definitions = {
        field_name: (field_info.annotation, field_info)
        for field_name, field_info in model.model_fields.items()
    }
    tool_type = create_model(
        f"{model.__name__}",
        __base__=base,
        __doc__=model.__doc__ if model.__doc__ else DEFAULT_TOOL_DOCSTRING,
        **cast(dict[str, Any], field_definitions),
    )
    for name, value in inspect.getmembers(model):
        if not hasattr(tool_type, name) or name in ["name", "description", "call"]:
            setattr(tool_type, name, value)
    return update_abstractmethods(tool_type)


BaseType = str | int | float | bool | list | set | tuple


def is_base_type(type_: Any) -> bool:
    """Check if a type is a base type."""
    base_types = {str, int, float, bool, list, set, tuple}
    return (
        (inspect.isclass(type_) and issubclass(type_, Enum))
        or type_ in base_types
        or get_origin(type_) in base_types.union({Literal, Union, Annotated})
    )


def convert_base_type_to_base_tool(
    schema: type[BaseType], base: type[BaseToolT]
) -> type[BaseToolT]:
    """Converts a `BaseType` to a `BaseToolT` type."""
    if get_origin(schema) == Annotated:
        schema.__name__ = get_args(schema)[0].__name__
    return create_model(
        schema.__name__,
        __base__=base,
        __doc__=DEFAULT_TOOL_DOCSTRING,
        value=(schema, ...),
    )
