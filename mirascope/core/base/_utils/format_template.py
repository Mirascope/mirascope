"""This module contains the `format_template` function."""

import inspect
from typing import Any

from .get_template_values import get_template_values
from .get_template_variables import get_template_variables


def format_template(template: str, attrs: dict[str, Any]) -> str:
    """Formats the given prompt `template`

    Args:
        template: The template to format.
        attrs: The attributes to use for formatting.

    Returns:
        The formatted template.

    """
    dedented_template = inspect.cleandoc(template).strip()
    template_vars = get_template_variables(dedented_template)

    values = get_template_values(template_vars, attrs)

    return dedented_template.format(**values)
