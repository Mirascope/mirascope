"""Internal Utilities."""

import inspect
import re
from string import Formatter
from textwrap import dedent
from typing import (
    Annotated,
    Any,
    Callable,
    ParamSpec,
    TypeVar,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from docstring_parser import parse
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from ..base.types import MessageParam

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
    for var in template_variables:
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
) -> list[MessageParam]:
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
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


def convert_function_to_base_model(
    fn: Callable[P, R], base: type[BaseModelT]
) -> type[BaseModelT]:
    """Constructst a `BaseModelT` type from the given function.

    This method expects all function parameters to be properly documented in identical
    order with identical variable names, as well as descriptions of each parameter.
    Errors will be raised if any of these conditions are not met.

    Args:
        fn: The function to convert.
        base: The `BaseModel` type to which the function is converted.

    Returns:
        The constructed `BaseModelT` type.

    Raises:
        ValueError: if the given function's parameters don't have type annotations.
        ValueError: if a given function's parameter is in the docstring args section but
            the name doesn't match the docstring's parameter name.
        ValueError: if a given function's parameter is in the docstring args section but
            doesn't have a docstring description.
    """
    docstring = None
    if fn.__doc__:
        docstring = parse(fn.__doc__)

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

    class BaseWithCall(base):
        def call(self) -> R:
            return fn(
                **{
                    self.model_fields[field_name].alias
                    if self.model_fields[field_name].alias
                    else field_name: getattr(self, field_name)
                    for field_name in self.model_dump(exclude={"tool_call"})
                }
            )

    return create_model(
        fn.__name__,
        __base__=BaseWithCall,
        __doc__=inspect.cleandoc(fn.__doc__) if fn.__doc__ else DEFAULT_TOOL_DOCSTRING,
        **cast(dict[str, Any], field_definitions),
    )


def convert_base_model_to_base_model(
    schema: type[BaseModel], base: type[BaseModelT]
) -> type[BaseModelT]:
    """Converts a `BaseModel` schema to a `BaseModelT` type.

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
        for field_name, field_info in schema.model_fields.items()
    }
    return create_model(
        f"{schema.__name__}",
        __base__=base,
        __doc__=schema.__doc__ if schema.__doc__ else DEFAULT_TOOL_DOCSTRING,
        **cast(dict[str, Any], field_definitions),
    )


BaseType = str | int | float | bool | list | set | tuple


def convert_base_type_to_tool(
    schema: type[BaseType], base: type[BaseModelT]
) -> type[BaseModelT]:
    """Converts a `BaseType` to a `BaseModelT` type."""
    if get_origin(schema) == Annotated:
        schema.__name__ = get_args(schema)[0].__name__
    return create_model(
        schema.__name__,
        __base__=base,
        __doc__=DEFAULT_TOOL_DOCSTRING,
        value=(schema, ...),
    )
