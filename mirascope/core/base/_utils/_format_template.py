"""This module contains the `format_template` function."""

from textwrap import dedent
from typing import Any

from ._get_template_values import get_template_values
from ._get_template_variables import get_template_variables


def format_template(template: str, attrs: dict[str, Any]) -> str:
    """Formats the given prompt `template`

    Args:
        template: The template to format.
        attrs: The attributes to use for formatting.

    Returns:
        The formatted template.

    """
    dedented_template = dedent(template).strip()
    template_vars = get_template_variables(dedented_template, True)

    values = get_template_values(template_vars, attrs)

    # Remove any special format specs that are actually invalid normally
    dedented_template = dedented_template.replace(":lists", "").replace(":list", "")

    return dedented_template.format(**values).strip()
