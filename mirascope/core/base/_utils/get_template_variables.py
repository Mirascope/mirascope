"""This module provides a function to get the variables in a template string."""

from string import Formatter


def get_template_variables(template: str) -> list[str]:
    """Returns the variables in the given template string.

    Args:
        template: The template string to parse.

    Returns:
        The variables in the template string.
    """
    return [var for _, var, _, _ in Formatter().parse(template) if var is not None]
