"""This module provides a function to parse messages from a prompt template."""

import re
from string import Formatter
from typing import Any, TypeVar

from pydantic import BaseModel

from ..message_param import BaseMessageParam
from .format_template import format_template

BaseToolT = TypeVar("BaseToolT", bound=BaseModel)


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
            content = format_template(match.group(2), attrs)
            if content:
                messages.append({"role": role, "content": content})
    if len(messages) == 0:
        messages.append(
            {
                "role": "user",
                "content": format_template(template, attrs),
            }
        )
    return messages
