"""Internal Utilities."""

import re
from string import Formatter
from textwrap import dedent
from typing import Any

from ..types import MessageParam


def format_prompt_template(template: str, attrs: dict[str, Any]) -> str:
    """Formats the given prompt `template`"""
    dedented_template = dedent(template).strip()
    template_vars = [
        var for _, var, _, _ in Formatter().parse(dedented_template) if var is not None
    ]

    values = {}
    for var in template_vars:
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
                )  # pragma: no cover
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
