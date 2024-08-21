"""This module provides a function to get the variables in a template string."""

from string import Formatter
from typing import Literal, overload


@overload
def get_template_variables(
    template: str, include_format_spec: Literal[True]
) -> list[tuple[str, str | None]]: ...


@overload
def get_template_variables(
    template: str, include_format_spec: Literal[False]
) -> list[str]: ...


def get_template_variables(
    template: str, include_format_spec: bool
) -> list[str] | list[tuple[str, str | None]]:
    """Returns the variables in the given template string.

    Args:
        template: The template string to parse.
        include_format_spec: A boolean indicating whether to include format specifications.

    Returns:
        The variables in the template string.
    """
    if include_format_spec:
        return [
            (var, format_spec)
            for _, var, format_spec, _ in Formatter().parse(template)
            if var
        ]
    else:
        return [var for _, var, _, _ in Formatter().parse(template) if var]
