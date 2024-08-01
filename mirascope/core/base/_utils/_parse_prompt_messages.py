"""This module provides a function to parse messages from a prompt template."""

import re
from typing import Any, TypeVar

from pydantic import BaseModel

from ..message_param import BaseMessageParam
from ._get_template_variables import get_template_variables
from ._parse_content_template import parse_content_template

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
        role, content_template = match.group(1).lower(), match.group(2).strip()
        if role == "messages":
            template_variables = get_template_variables(content_template, False)
            if template_variables[0].startswith("self"):
                if "self" not in attrs:
                    raise ValueError(
                        "MESSAGES keyword used with `self.` but `self` was not found."
                    )
                attr = getattr(attrs["self"], template_variables[0][5:])
            else:
                attr = attrs[template_variables[0]]
            if attr is None or not isinstance(attr, list):
                raise ValueError(
                    f"MESSAGES keyword used with attribute `{template_variables[0]}`"
                    ", which is not a `list` of messages."
                )
            messages += attr
        else:
            content = parse_content_template(role, content_template, attrs)
            if content:
                messages.append(content)
    if len(messages) == 0:
        content = parse_content_template("user", template, attrs)
        if content:
            messages.append(content)
    return messages
